const test = require('node:test');
const assert = require('node:assert/strict');

function invokeConfigApi({ method = 'GET', origin, env = {} } = {}) {
  const keys = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_PUBLISHABLE_KEY', 'SUPABASE_SERVICE_ROLE_KEY', 'AURA_ALLOWED_ORIGIN'];
  const previous = Object.fromEntries(keys.map(key => [key, process.env[key]]));
  keys.forEach(key => delete process.env[key]);
  Object.assign(process.env, env);
  delete require.cache[require.resolve('../api/config')];
  const handler = require('../api/config');
  const headers = {};
  let statusCode;
  let body;
  const request = { method, headers: origin ? { origin } : {} };
  const response = {
    setHeader(name, value) { headers[name] = value; },
    status(code) { statusCode = code; return this; },
    json(value) { body = value; return value; }
  };
  handler(request, response);
  keys.forEach(key => {
    if (previous[key] === undefined) delete process.env[key];
    else process.env[key] = previous[key];
  });
  return { statusCode, body, headers };
}

test('configuration endpoint returns only the public Supabase URL and key', () => {
  const response = invokeConfigApi({
    env: {
      SUPABASE_URL: 'https://campus.supabase.co',
      SUPABASE_ANON_KEY: 'public-key',
      SUPABASE_SERVICE_ROLE_KEY: 'never-return-this'
    }
  });
  assert.equal(response.statusCode, 200);
  assert.deepEqual(response.body, {
    supabaseUrl: 'https://campus.supabase.co',
    supabaseAnonKey: 'public-key'
  });
  assert.equal(response.headers['Cache-Control'], 'no-store, max-age=0');
});

test('configuration endpoint refuses missing settings and non-GET requests', () => {
  assert.equal(invokeConfigApi().statusCode, 503);
  assert.equal(invokeConfigApi({ method: 'POST' }).statusCode, 405);
});

test('configuration endpoint rejects non-HTTPS project URLs and unexpected origins', () => {
  assert.equal(invokeConfigApi({ env: {
    SUPABASE_URL: 'http://campus.supabase.co',
    SUPABASE_ANON_KEY: 'public-key'
  } }).statusCode, 503);
  assert.equal(invokeConfigApi({
    origin: 'https://attacker.example',
    env: {
      SUPABASE_URL: 'https://campus.supabase.co',
      SUPABASE_ANON_KEY: 'public-key',
      AURA_ALLOWED_ORIGIN: 'https://aura-campus-three.vercel.app'
    }
  }).statusCode, 403);
});
