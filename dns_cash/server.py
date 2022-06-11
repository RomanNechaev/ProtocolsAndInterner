import socket
from parse.response import Response


class Server:
    def __init__(self):
        self.port = 53
        self.local_ip = '127.0.0.1'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        self.sock.bind((self.local_ip, self.port))
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                response = Response.make_response(data)
                self.sock.sendto(response, addr)
            except KeyboardInterrupt:
                break


if __name__ == '__main__':
    s = Server()
    s.run()
