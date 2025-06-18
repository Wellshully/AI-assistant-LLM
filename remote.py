import socket

s = socket.socket()
s.connect(("192.168.66.14", 5052))
s.send(b"Zxc9249258852xc")
