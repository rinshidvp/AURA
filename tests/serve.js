const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml'
};

http.createServer((request, response) => {
  const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);

  if (pathname === '/api/config') {
    response.writeHead(503, { 'Content-Type': 'application/json; charset=utf-8' });
    response.end(JSON.stringify({ error: 'Portal authentication is not configured for the local static preview.' }));
    return;
  }

  const requestedPath = pathname === '/' ? '/index.html' : pathname;
  const absolutePath = path.resolve(root, `.${requestedPath}`);

  if (!absolutePath.startsWith(root + path.sep) && absolutePath !== path.join(root, 'index.html')) {
    response.writeHead(403).end('Forbidden');
    return;
  }

  fs.readFile(absolutePath, (error, content) => {
    if (error) {
      response.writeHead(404).end('Not found');
      return;
    }
    response.writeHead(200, { 'Content-Type': contentTypes[path.extname(absolutePath)] || 'application/octet-stream' });
    response.end(content);
  });
}).listen(4173, '127.0.0.1');
