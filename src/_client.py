import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 5353))

s.send(bytes("POST /dns-query HTTP/1.1\r\n\r\nwww.fit.vutbr.cz:PTR\nwww.google.com:A\nwww.brno.cz:A\r\nwww.facebook.com:A\n34.213.147.57:A\n147.229.2.90:PTR\n", "utf-8"))
answer = s.recv(1024).decode("utf-8")
print(answer)
