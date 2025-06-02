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
full_room_list = []

def broadcast_lobby_update(room_num):
    print(room_num)
    if room_num in room_members:
        players_info = [
            {"player_id": m["player_id"], "name": m["name"], "skin_id": m["skin_id"], "ready": m["ready"], "host":m["host"]}
            for m in room_members[room_num]
        ]
        print(room_members[room_num])
        message = json.dumps({"type": "LobbyUpdate", "players": players_info})
        for m in room_members[room_num]:
            try:
                m["conn"].send(message.encode())
            except:
                pass

def notify_room_closed(room_num):
    """Notify all members that the room has been closed"""
    if room_num in room_members:
        message = json.dumps({"type": "RoomClosed"})
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
            
            # Handle multiple concatenated messages
            messages = []
            buffer = data
            
            # Split concatenated messages
            while buffer:
                # Find the next command by looking for known prefixes
                commands = ["Game Room", "Create Room", "Join Room", "Leave Room", "Remove Room", "Update", "Kick"]
                next_pos = len(buffer)
                
                for cmd in commands:
                    pos = buffer.find(cmd + ":", 1)  # Start from position 1 to skip current command
                    if pos > 0 and pos < next_pos:
                        next_pos = pos
                
                # Extract current message
                if next_pos < len(buffer):
                    messages.append(buffer[:next_pos])
                    buffer = buffer[next_pos:]
                else:
                    messages.append(buffer)
                    break
            
            # Process each message
            for message in messages:
                print("Received:", message)
                parts = message.split(":")
                command = parts[0]
                reply = ""

                if command == "Game Room":
                    reply = json.dumps(room_list)
                    conn.sendall(reply.encode())

                elif command == "Create Room":
                    room_num, room_password = parts[1], parts[2] if len(parts) > 2 else ""
                    room_id = str(len(room_list) + 1)
                    room_list.append(f"{room_id}:{room_num}:{room_password}:{1}")
                    room_members[room_num] = [{"conn":conn, "player_id":0, "name":"Player 1", "skin_id":0, "ready":False, "host":True}]
                    conn.sendall(f"Joined:{room_num}:0:host".encode())
                    broadcast_lobby_update(room_num)

                elif command == "Join Room":
                    room_num = parts[1]
                    if room_num in room_members and len(room_members[room_num]) < 4:
                        player_id = len(room_members[room_num])
                        room_members[room_num].append({"conn":conn, "player_id":player_id, "name":f"Player {player_id+1}", "skin_id":0, "ready":False, "host":False})
                    
                        # Update capacity in room_list
                        for i in range(len(room_list)):
                            room_id, name, password, capacity = room_list[i].split(":")
                            if name == room_num:
                                new_capacity = str(len(room_members[room_num]))
                                updated_room = f"{room_id}:{name}:{password}:{new_capacity}"

                                # If room is now full, move it to full_room_list and remove from room_list
                                if int(new_capacity) >= 4:
                                    full_room_list.append(updated_room)
                                    room_list.pop(i)
                                else:
                                    room_list[i] = updated_room
                                break

                        conn.sendall(f"Joined:{room_num}:{player_id}:member".encode())
                        broadcast_lobby_update(room_num)

                elif command == "Leave Room":
                    room_num, pid = parts[1], int(parts[2])
                    if room_num in room_members:
                        room_members[room_num] = [m for m in room_members[room_num] if not (m["conn"] == conn and m["player_id"] == pid)]
                        
                        # Shift IDs
                        for i, m in enumerate(room_members[room_num]):
                            m["player_id"] = i
                        
                        # Update capacity in room_list and full_room_list
                        new_capacity = len(room_members[room_num])
                        for i in range(len(room_list)):
                            room_id, name, password, capacity = room_list[i].split(":")
                            if name == room_num:
                                room_list[i] = f"{room_id}:{name}:{password}:{new_capacity}"
                                break

                        for i in range(len(full_room_list)):
                            room_id, name, password, capacity = full_room_list[i].split(":")
                            if name == room_num:
                                # Room is no longer full, move back to room_list
                                full_room = full_room_list.pop(i)
                                room_list.append(f"{room_id}:{name}:{password}:{new_capacity}")
                                break
                        broadcast_lobby_update(room_num)

                elif command == "Remove Room":
                    room_num = parts[1]
                    # Notify all members before removing the room
                    notify_room_closed(room_num)
                    
                    # Remove from room lists
                    room_list = [r for r in room_list if room_num not in r]
                    full_room_list = [r for r in full_room_list if room_num not in r]
                    
                    # Remove room members
                    if room_num in room_members:
                        del room_members[room_num]

                elif command == "Update":
                    if len(parts) >= 6:
                        room_num, pid, name, skin_id, ready_str = parts[1], int(parts[2]), parts[3], int(parts[4]), parts[5]
                        
                        # Check if room still exists
                        if room_num not in room_members:
                            print(f"Room {room_num} no longer exists, ignoring update")
                            continue
                            
                        ready = ready_str == "True"

                        for m in room_members.get(room_num, []):
                            if m["player_id"] == pid:
                                m["name"] = name
                                m["skin_id"] = skin_id
                                m["ready"] = ready
                                break
                        print("Updated")
                        broadcast_lobby_update(room_num)

                elif command == "Kick":
                    room_num, target_id = parts[1], int(parts[2])

                if room_num in room_members:
                    for i, m in enumerate(room_members[room_num]):
                        if m["player_id"] == target_id:
                            try:
                                m["conn"].send("Kicked".encode())  # Optional: notify the kicked player
                            except:
                                pass
                            room_members[room_num].pop(i)
                            print(f"Player {target_id} kicked. Remaining players: {len(room_members[room_num])}")
                            
                            # Shift remaining player IDs
                            for j, player in enumerate(room_members[room_num]):
                                player["player_id"] = j
                            broadcast_lobby_update(room_num)
                            break

                    new_capacity = len(room_members[room_num])
                    for i in range(len(room_list)):
                        room_id, name, password, capacity = room_list[i].split(":")
                        if name == room_num:
                            room_list[i] = f"{room_id}:{name}:{password}:{new_capacity}"
                            break
                    print(room_list)

        
        except Exception as e:
            print("Error:", e)
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))