import socket
import json

class Network:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "26.189.170.88" # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
                                    # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
                                    # ipv4 address. This feild will be the same for all your clients.
        self.port = 5555
        self.addr = (self.host, self.port)
        self.net_id = None
        if self.connect():
            print("Connect")
        else:
            print("Unsuccessful connect")

    def connect(self):
        try:
            self.client.connect(self.addr)
            return True
        except Exception as e:
            print("Connection failed:", e)
            return False

    def send(self, data):
        try:
            self.client.send(str.encode(data))
        except socket.error as e:
            return str(e)
        
    def send_receive(self, data):
        self.client.send(str.encode(data))
        reply = self.client.recv(2048).decode()
        self.net_id = reply.split(":")[2]
        return reply

    def receive_room_list(self):
        try:
            raw_data = self.client.recv(2048).decode()
            if raw_data:
                return json.loads(raw_data)
        except Exception as e:
            print("Room list receive error:", e)
            return []
