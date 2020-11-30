# Test socket 2020-09-23
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import socket

HOST = '127.0.0.1'
PORT = 5000
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"


def send_messsage(mes):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(mes)
    # data = s.recv(BUFFER_SIZE)
    s.close()
    # print("received data:", data)


# print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

if __name__ == '__main__':
    print('Run mode.')
    mes = b'KV05'
    print(f'mes={mes}.')
    send_messsage(mes)
    print('End')
