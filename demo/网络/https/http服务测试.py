from http.server import HTTPServer, BaseHTTPRequestHandler

class EchoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 设置响应状态码
        self.send_response(200)
        # 设置响应头（纯文本格式）
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # 返回固定内容
        self.wfile.write(b"helloworld\n")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, EchoHandler)
    print(f"✅ 服务已启动，访问地址: http://localhost:{port}/echo")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()