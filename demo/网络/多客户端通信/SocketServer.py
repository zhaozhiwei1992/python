"""
聊天组

支持多个客户端注册

服务器负责消息分发, 客户端发过来的消息, 会分发给所有注册的人

"""

import select
import socket
import queue
from time import sleep


class Server:
    def __init__(self):
        # Create a TCP/IP
        self.client_address = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(False)

        # Bind the socket to the port
        server_address = (socket.gethostname(), 12346)
        print('starting up on %s port %s' % server_address)
        self.server.bind(server_address)

        # Listen for incoming connections
        self.server.listen(5)

        # Sockets from which we expect to read
        self.inputs = [self.server]

        # Sockets to which we expect to write
        # 处理要发送的消息
        self.outputs = []

        # 使用queue, 消息只保留一次
        # 记录消息是哪个客户端发的，自己发的消息之发给别人
        self.message_queues = {}

    def run(self):
        while True:
            # Wait for at least one of the sockets to be ready for processing
            print('waiting for the next event')
            # 开始select 监听, 对input_list 中的服务器端server 进行监听
            # 一旦调用socket的send, recv函数，将会再次调用此模块
            # readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
            # 这里是群聊，不需要output, 只要input进来的都是兄弟
            readable, writable, exceptional = select.select(self.inputs, [], self.inputs)
            # Handle inputs
            # 循环判断是否有客户端连接进来, 当有客户端连接进来时select 将触发
            for s in readable:
                # 判断当前触发的是不是服务端对象, 当触发的对象是服务端对象时,说明有新客户端连接进来了
                # 表示有新用户来连接, 由客户端的s.connect(server_address)触发
                if s is self.server:
                    # A "readable" socket is ready to accept a connection
                    connection, self.client_address = s.accept()
                    print('connection from', self.client_address)
                    # this is connection not server
                    connection.setblocking(0)
                    # 将客户端对象也加入到监听的列表中, 当客户端发送消息时 select 将触发
                    self.inputs.append(connection)

                    # Give the connection a queue for data we want to send
                    # 为连接的客户端单独创建一个消息队列，用来保存客户端发送的消息
                    self.message_queues[connection] = queue.Queue()
                else:
                    # 由于客户端连接进来时服务端接收客户端连接请求，将客户端加入到了监听列表中(input_list), 客户端发送消息将触发
                    # 客户端对象send消息触发, 这里就可以接收了
                    data = str(s.recv(1024), encoding='utf-8')
                    # 收到客户端消息
                    if data != '':
                        # A readable client socket has data
                        print('received "%s" from %s' % (data, s.getpeername()))
                        # 将收到的消息放入到相对应的socket客户端的消息队列中
                        self.message_queues[s].put(data)

                        #   群发其他客户端
                        self.sendAll()

            # Handle outputs
            # 如果是注册到写出的客户端有变化时触发, output这里是去掉server的input
            for s in writable:
                try:
                    send_data = '呵呵'
                    # print "sending %s to %s " % (send_data, s.getpeername)
                    # print "send something"
                    s.send(send_data)
                    # del message_queues[s]
                    # writable.remove(s)
                    # print "Client %s disconnected" % (client_address)
                except queue.Empty:
                    # 客户端连接断开了
                    print("%s" % (s.getpeername()))
                    self.outputs.remove(s)

            # # Handle "exceptional conditions"
            # 处理异常的情况
            for s in exceptional:
                print('exception condition on', s.getpeername())
                # Stop listening for input on the connection
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()

                # Remove message queue
                del self.message_queues

            sleep(1)

    def sendAll(self):
        # 如果消息队列中有消息,从消息队列中获取要发送的消息
        for key in self.message_queues:
            # print(key)
            # print(self.message_queues[key])
            send_data = ''
            if self.message_queues[key] is not None:
                # 便利所有注册的socket
                try:
                    send_data = self.message_queues[key].get_nowait()
                except queue.Empty:
                    print("队列空了")
                for s in self.inputs:
                    # 不发给服务端和他自己(key, 表示这消息是自己发过来的)
                    if s is not self.server and s is not key and send_data != '':
                        print("send to %s, message %s" % (s, send_data))
                        s.send(bytes(send_data, 'utf-8'))


if __name__ == '__main__':
    Server().run()
