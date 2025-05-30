import socket
import json
from _thread import *
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '26.189.170.88'
port = 5555

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

# listen up for 2 connections
s.listen(4)
print("Waiting for a connection")

room_list = [] # list of rooms
room_members = {}
pos = ["0:50,50", "1:100,100"] # first game of multi
def threaded_client(conn):
    global room_list, room_members, pos
    reply = ''

    while True:
        
        try:
            data = conn.recv(2048) # receive data from client
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                command = reply.split(":")[0]

                if command == "Game Room":
                    reply = json.dumps(room_list)

                if command == "Create Room":
                    room_id = str(len(room_list)+1)
                    room_num = reply.split(":")[1].split(",")[0]

                    if reply.split(":")[1].split(",")[1] != " ":
                        room_password = reply.split(":")[1].split(",")[1]
                        room_list.append(f"{room_id}: {room_num}, {room_password}")
                    else:
                        room_list.append(f"{room_id}: {room_num},")

                    room_members[room_num] = [conn]
                    
                    player_id = 0
                    reply = f"Joined:{room_num}:{player_id}:host"
                    print(reply)

                if command == "Join Room":
                    room_num = reply.split(":")[1]

                    if room_num in room_members and len(room_members[room_num]) < 4:
                        player_id = len(room_members[room_num])
                        room_members[room_num].append(conn)
                        reply = f"Joined:{room_num}:{player_id}:member"
                    
                if command == "Remove Room":
                    room_num = reply.split(":")[1]

                    # Remove from room_list
                    room_list = [room for room in room_list if not room.split(": ")[1].split(",")[0] == room_num]
                    print(f"Room{room_num} removed")

                    # Remove from room_members
                    if room_num in room_members:
                        del room_members[room_num]

                if command == "Leave Room":
                    room_num = reply.split(":")[1]
                    player_id = reply.split(":")[2]

                    if room_num in room_members:
                        members = room_members[room_num]

                        # Remove player with matching conn or player_id
                        for i, player in enumerate(members):
                            if player["player_id"] == player_id and player["conn"] == conn:
                                members.pop(i)
                                break

                        # Shift player IDs down
                        for idx, player in enumerate(members):
                            player["player_id"] = idx
                    
            conn.sendall(reply.encode())
        except:
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))