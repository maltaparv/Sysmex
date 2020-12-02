# https://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python
# https://github.com/eliben/code-for-blog/tree/master/2011/socket_client_thread_sample
""" 
Test server for the client thread sample
Eli Bendersky (eliben@gmail.com)
This code is in the public domain
"""
from socket import *
import time
myHost = ''
myPort = 50005

sockobj = socket(AF_INET, SOCK_STREAM)
sockobj.bind((myHost, myPort))
sockobj.listen(2)

connection, address = sockobj.accept()
print('Server connected by', address)

d = connection.recv(1024)
print(f'Получено:\n{d.decode("cp1251")}')

time.sleep(1.5)
msg = 'Cock-A-Doodle-Doo! Кукареку! :)'.encode('1251')
connection.send(msg)
print(f'send:\n{msg.decode("1251")}')
