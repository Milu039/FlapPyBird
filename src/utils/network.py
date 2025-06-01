import socket
import threading
import json

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "26.189.170.88"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = None
        self.lobby_state = []
        self.room_num = None
        self.running = True

        try:
            self.client.connect(self.addr)
        except Exception as e:
            print("Failed to connect:", e)

    def send(self, data):
        self.client.send(data.encode())

    def send_receive_id(self, data):
        self.send(data)
        reply = self.client.recv(2048).decode()
        self.id = reply.split(":")[2]
        return reply

    def receive_room_list(self):
        try:
            data = self.client.recv(2048).decode()
            return json.loads(data)
        except:
            return []

    def listen_for_lobby_updates(self):
            try:
                data = self.client.recv(2048).decode()
                if data == "Kicked":
                    self.kicked = True
                    return
                message = json.loads(data)
                if message.get("type") == "LobbyUpdate":
                    self.lobby_state = message["players"]
                    print("Updated Lobby State:", self.lobby_state)
            except:
                return "Error Lobby Update"