import socket


class Network:
    def __init__(self, host="localhost"):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host  # Default to localhost, but can be passed in
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()
        
    def connect(self):
        """Connect to the server and get the player ID"""
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(f"Connection Error: {e}")
            return "-1"  # Return invalid ID on connection failure
            
    def send(self, data):
        """
        Send data to server and receive response
        :param data: str - Data to send in format "id:x,y,rot"
        :return: str - Data received from server
        """
        try:
            self.client.send(str.encode(data))
            return self.client.recv(4096).decode()
        except socket.error as e:
            print(f"Send Error: {e}")
            return ""