import http.server
import socketserver
import socket

PORT = 8080
HTML = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>IPv6 Test</title></head>
<body style="font-family:sans-serif;text-align:center;padding-top:100px">
<h1>IPv6 works!</h1>
<p>You reached this server via IPv6.</p>
</body>
</html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

class V6Server(socketserver.TCPServer):
    address_family = socket.AF_INET6
    allow_reuse_address = True

with V6Server(("::", PORT), Handler) as httpd:
    print(f"Serving on http://[::]:{PORT}")
    print(f"Access via: http://[2408:8226:250:1d40:6462:a3c2:f8b4:d545]:{PORT}")
    httpd.serve_forever()
