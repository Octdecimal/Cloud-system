import socket
import threading

class P2PNode:
    def __init__(self, port, peers):
        self.port = port
        self.peers = peers
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('172.17.0.2', self.port)) #這是本節點的 IP

    def start(self):
        threading.Thread(target=self._listen).start()
        threading.Thread(target=self._send_messages).start()

    def _listen(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            print(f"Received {data.decode('utf-8')} from {addr}")

    def _send_messages(self):
        while True:
            message = input("Enter a message: ")
            for peer in self.peers:
                self.sock.sendto(message.encode('utf-8'), peer)

if __name__ == '__main__':
    port = 8001 #本節點的port 
    peers = [('172.17.0.4', 8001), ('172.17.0.3', 8001)]  #跟另外二個IP:8001 節點通信
    node = P2PNode(port, peers)
    node.start()

