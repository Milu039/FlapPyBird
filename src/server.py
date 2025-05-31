import socket
import json
from _thread import start_new_thread

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = '0.0.0.0'
port = 5555

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(4)
print("Waiting for a connection")

room_list = []
room_members = {}

def broadcast_lobby_update(room_num):
    if room_num in room_members:
        players_info = [
            {"player_id": m["player_id"], "name": m["name"], "skin_id": m["skin_id"]}
            for m in room_members[room_num]
        ]
        print(room_members[room_num])
        message = json.dumps({"type": "LobbyUpdate", "players": players_info})
        for m in room_members[room_num]:
            try:
                m["conn"].send(message.encode())
            except:
                pass

def threaded_client(conn):
    global room_list, room_members

    while True:
        try:
            data = conn.recv(2048).decode("utf-8")
            if not data:
                break
            print("Received:", data)
            parts = data.split(":")
            command = parts[0]
            reply = ""

            if command == "Game Room":
                reply = json.dumps(room_list)
                conn.sendall(reply.encode())

            elif command == "Create Room":
                room_num, room_password = parts[1].split(",")
                room_id = str(len(room_list) + 1)
                room_list.append(f"{room_id}: {room_num}, {room_password}")
                room_members[room_num] = [{"conn": conn, "player_id": 0, "name": "Player 1", "skin_id": 0}]
                conn.sendall(f"Joined:{room_num}:0:host".encode())
                broadcast_lobby_update(room_num)

            elif command == "Join Room":
                room_num = parts[1]
                if room_num in room_members and len(room_members[room_num]) < 4:
                    player_id = len(room_members[room_num])
                    room_members[room_num].append({"conn": conn, "player_id": player_id, "name": f"Player {player_id+1}", "skin_id": 0})
                    conn.sendall(f"Joined:{room_num}:{player_id}:member".encode())
                    broadcast_lobby_update(room_num)

            elif command == "Leave Room":
                room_num, pid = parts[1], int(parts[2])
                if room_num in room_members:
                    room_members[room_num] = [m for m in room_members[room_num] if not (m["conn"] == conn and m["player_id"] == pid)]
                    # Shift IDs
                    for i, m in enumerate(room_members[room_num]):
                        m["player_id"] = i
                    broadcast_lobby_update(room_num)

            elif command == "Remove Room":
                room_num = parts[1]
                room_list = [r for r in room_list if room_num not in r]
                if room_num in room_members:
                    del room_members[room_num]

            elif command == "Update":
                room_num, pid, name, skin_id = parts[1], int(parts[2]), parts[3], int(parts[4])

                for m in room_members.get(room_num, []):
                    if m["player_id"] == pid:
                        m["name"] = name
                        m["skin_id"] = skin_id
                        break
                broadcast_lobby_update(room_num)
        
        except Exception as e:
            print("Error:", e)
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))