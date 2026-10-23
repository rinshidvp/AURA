const allowedOrigin = process.env.AURA_ALLOWED_ORIGIN;

module.exports = function handler(request, response) {
  if (request.method !== 'GET') {
    response.setHeader('Allow', 'GET');
    return response.status(405).json({ error: 'Method not allowed.' });
  }

  if (allowedOrigin && request.headers.origin && request.headers.origin !== allowedOrigin) {
    return response.status(403).json({ error: 'Origin is not allowed.' });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || process.env.SUPABASE_PUBLISHABLE_KEY;

  response.setHeader('Cache-Control', 'no-store, max-age=0');
  response.setHeader('Vary', 'Origin');
  if (allowedOrigin) response.setHeader('Access-Control-Allow-Origin', allowedOrigin);

  if (!supabaseUrl || !supabaseAnonKey) {
    return response.status(503).json({ error: 'Portal authentication is not configured.' });
  }

  try {
    const parsedUrl = new URL(supabaseUrl);
    if (parsedUrl.protocol !== 'https:' && parsedUrl.hostname !== 'localhost') {
      return response.status(503).json({ error: 'Supabase URL must use HTTPS.' });
    }
  } catch {
    return response.status(503).json({ error: 'Supabase URL is invalid.' });
  }

  return response.status(200).json({ supabaseUrl, supabaseAnonKey });
};
