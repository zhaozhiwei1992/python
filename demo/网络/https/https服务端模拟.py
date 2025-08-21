"""

启动服务：
python https_echo_server.py
首次运行会自动生成自签名证书（server.pem）
测试接口：
# GET 请求测试
curl -k https://localhost:4443/any_path

# POST 请求测试
curl -k -X POST -d "test data" https://localhost:4443/api/echo
"""
import http.server
import ssl
import os


class EchoHandler(http.server.BaseHTTPRequestHandler):
    """处理所有请求的 Echo 处理器"""

    def do_GET(self):
        """处理 GET 请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # 返回请求信息
        response = f"GET请求成功\n路径: {self.path}\n"
        self.wfile.write(response.encode())

    def do_POST(self):
        """处理 POST 请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # 返回请求体和路径
        response = f"POST请求成功\n路径: {self.path}\n内容: {post_data.decode()}\n"
        self.wfile.write(response.encode())


def generate_self_signed_cert():
    """生成自签名证书（测试用）"""
    if not os.path.exists("server.pem"):
        os.system(
            "openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj '/CN=localhost'")
        os.system("cat key.pem cert.pem > server.pem")
        os.remove("key.pem")
        os.remove("cert.pem")
    return "server.pem"


if __name__ == '__main__':
    # 生成自签名证书
    cert_file = generate_self_signed_cert()

    # 配置服务器
    host, port = '0.0.0.0', 4443
    server = http.server.HTTPServer((host, port), EchoHandler)

    # 启用 HTTPS
    server.socket = ssl.wrap_socket(
        server.socket,
        server_side=True,
        keyfile=cert_file,
        certfile=cert_file,
        ssl_version=ssl.PROTOCOL_TLS
    )

    print(f"✅ HTTPS服务已启动: https://{host}:{port}")
    print("测试命令: curl -k -X POST -d 'hello' https://localhost:4443/api/echo")
    server.serve_forever()