# coding: utf-8
import socket

from time import sleep

messages = ['This is the message ', 'It will be sent ', 'in parts ', ]

server_address = (socket.gethostname(), 12346)

# Connect thesocket to the port where the server is listening
print('connecting to %s port %s' % server_address)

# 连接到服务器
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(server_address)


def send():
    message = "用户1: hello world, send message"
    # Send messages on both sockets
    print('%s: sending "%s"' % (s.getsockname(), message))
    s.send(bytes(message, 'utf-8'))


def receive():
    data = str(s.recv(1024), encoding='utf-8')
    print('%s: received "%s"' % (s.getsockname(), data))
    # if data != "":
    #     print('closingsocket', s.getsockname())
    #     s.close()


if __name__ == '__main__':
    while True:
        send()
        sleep(2)
        receive()
        sleep(2)
