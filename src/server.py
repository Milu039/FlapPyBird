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
room_states = {}
ready_players = {}
ready_next_index = {}
early_ready = {}
default_pos = ["0:50:50:0", "1:100:100:0", "2:150:150:0","3:200:200:0"]

def broadcast_lobby_update(room_num):
    if room_num in room_members:
        players_info = [
            {
                "player_id": m["player_id"],
                "name": m["name"],
                "skin_id": m["skin_id"],
                "ready": m["lobby"]["ready"],
                "host": m["lobby"]["host"]
            }
            for m in room_members[room_num]
        ]
        message = json.dumps({"type": "LobbyUpdate", "players": players_info})

        for m in room_members[room_num]:
            try:
                m["conn"].send(message.encode())
            except:
                pass

def broadcast_game_update(room_num):
    if room_num in room_members:
        game_info = [
            {
                "player_id": m["player_id"],
                "name": m["name"],
                "skin_id": m["skin_id"],
                "x": m["game"]["x"],
                "y": m["game"]["y"],
                "rot": m["game"]["rot"],
            }
            for m in room_members[room_num]
        ]
        print(game_info)
        message = json.dumps({"type": "GameUpdate", "players": game_info})
        for m in room_members[room_num]:
            try:
                m["conn"].send(message.encode())
            except:
                pass

def notify_room_closed(room_num):
    """Notify all members that the room has been closed"""
    if room_num in room_members:
        message = json.dumps({"type": "RoomClosed"})
        print(message)
        for m in room_members[room_num]:
            try:
                m["conn"].send(message.encode())
            except:
                pass

def threaded_client(conn):
    global room_list, room_members, full_room_list, room_states, ready_players, ready_next_index, early_ready, default_pos

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
                room_num, room_password = parts[1], parts[2]
                room_id = str(len(room_list) + 1)
                room_list.append(f"{room_id}:{room_num}:{room_password}:{1}")
                room_members[room_num] = [{
                    "conn": conn,
                    "player_id": 0,
                    "name": "Player 1",
                    "skin_id": 0,
                    "lobby": {"ready": False, "host": True},
                    "game": {"x": 0, "y": 0, "rot": 0.0}
                }]
                room_states[room_num] = {"default_initialized": False,}
                conn.sendall(f"Joined:{room_num}:0:host".encode())
                broadcast_lobby_update(room_num)

            elif command == "Join Room":
                room_num = parts[1]
                
                if room_num in room_members and len(room_members[room_num]) < 4:
                    player_id = len(room_members[room_num])
                    room_members[room_num].append({
                        "conn":conn, 
                        "player_id":player_id, 
                        "name":f"Player {player_id+1}", 
                        "skin_id":0, 
                        "lobby": {"ready": False, "host": False},
                        "game": {"x": 0, "y": 0, "rot": 0.0}
                        })

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
                        break  # Done, exit loop

                conn.sendall(f"Joined:{room_num}:{player_id}:member".encode())
                broadcast_lobby_update(room_num)

            elif command == "Leave Room":
                room_num, pid = parts[1], int(parts[2])
                if room_num in room_members:
                    # Remove player
                    room_members[room_num] = [m for m in room_members[room_num] if not (m["conn"] == conn and m["player_id"] == pid)]

                    # Reassign player IDs
                    for i, m in enumerate(room_members[room_num]):
                        m["player_id"] = i

                    new_capacity = len(room_members[room_num])

                    # Update room_list
                    for i in range(len(room_list)):
                        room_id, name, password, capacity = room_list[i].split(":", 3)
                        if name == room_num:
                            room_list[i] = f"{room_id}:{name}:{password}:{new_capacity}"
                            break

                    # Move from full_room_list to room_list if necessary
                    for i in range(len(full_room_list)):
                        room_id, name, password, capacity = full_room_list[i].split(":", 3)
                        if name == room_num:
                            full_room_list.pop(i)
                            room_list.append(f"{room_id}:{name}:{password}:{new_capacity}")
                            break

                    # Optionally delete room if empty
                    if new_capacity == 0:
                        room_members.pop(room_num, None)
                        room_list = [r for r in room_list if room_num not in r]
                        full_room_list = [r for r in full_room_list if room_num not in r]
                        return

                    broadcast_lobby_update(room_num)

            elif command == "Remove Room": # need test
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
                room_num, pid, name, skin_id, ready_str = parts[1], int(parts[2]), parts[3], int(parts[4]), parts[5]
                ready = ready_str == "True"

                for m in room_members.get(room_num, []):
                    if m["player_id"] == pid:
                        m["name"] = name
                        m["skin_id"] = skin_id
                        m["lobby"]["ready"] =  ready
                        break
                #print("Updated")
                broadcast_lobby_update(room_num)
            
            elif command == "Start":
                room_list = [r for r in room_list if room_num not in r]
                # Reset ready info
                ready_players[room_num] = set()
                ready_next_index[room_num] = 0

                # Send "Start" to all players
                for player in room_members[room_num]:
                    try:
                        player["conn"].send("Start".encode())
                    except:
                        continue

                # Prompt first player to send Ready
                first_player = room_members[room_num][0]
                try:
                    first_player["conn"].send(f"ReadyNext:{first_player['player_id']}".encode())
                except:
                    pass

            elif command == "Ready":
                room_num, player_id = parts[1], int(parts[2])

                if room_num not in ready_next_index:
                    ready_next_index[room_num] = 0

                players = room_members.get(room_num, [])
                current_index = ready_next_index[room_num]

                if current_index < len(players):
                    expected_player_id = players[current_index]["player_id"]

                    if player_id == expected_player_id:
                        # Accept the ready in turn
                        ready_players.setdefault(room_num, set()).add(player_id)
                        ready_next_index[room_num] += 1

                        # Check if next player had already sent Ready early
                        while ready_next_index[room_num] < len(players):
                            next_player = players[ready_next_index[room_num]]
                            next_id = next_player["player_id"]

                            if room_num in early_ready and next_id in early_ready[room_num]:
                                # Remove from early_ready and process
                                early_ready[room_num].remove(next_id)
                                ready_players[room_num].add(next_id)
                                ready_next_index[room_num] += 1
                            else:
                                # Prompt the next player
                                try:
                                    next_player["conn"].send(f"ReadyNext:{next_id}".encode())
                                except:
                                    pass
                                break  # Exit loop once next_player is notified

                        # If all players are ready
                        if ready_next_index[room_num] >= len(players):
                            for player in players:
                                try:
                                    player["conn"].send("AllReady".encode())
                                except:
                                    pass

                    else:
                        # Save this player's early Ready
                        early_ready.setdefault(room_num, set()).add(player_id)
                        print(f"[INFO] Queued early Ready from player {player_id} (waiting turn)")


            elif parts[0] in room_members:
                room_num = parts[0]
                player_id = int(parts[1])

                # On first call, send default positions (for countdown)
                if not room_states[room_num]["default_initialized"]:
                    for pos in default_pos:
                        idx, x, y, rot = pos.split(":")
                        idx = int(idx)
                        if idx < len(room_members[room_num]):
                            room_members[room_num][idx]["game"]["x"] = float(x)
                            room_members[room_num][idx]["game"]["y"] = float(y)
                            room_members[room_num][idx]["game"]["rot"] = float(rot)

                    room_states[room_num]["default_initialized"] = True
                    broadcast_game_update(room_num)

                else:
                    # After countdown, handle actual player game data
                    x = float(parts[2])
                    y = float(parts[3])
                    rot = float(parts[4])

                    for m in room_members[room_num]:
                        if m["player_id"] == player_id:
                            m["game"]["x"] = x
                            m["game"]["y"] = y
                            m["game"]["rot"] = rot
                            break

                    broadcast_game_update(room_num)

            elif command == "Pipe":
                room_num, gap_y = parts[1], parts[2]
                for player in room_members.get(room_num, []):
                    try:
                        player["conn"].send(f"Pipe:{room_num}:{gap_y}:".encode())
                    except:
                        pass
            
            elif command == "Restart":
                if room_num in room_members:
                    print(f"[INFO] Host restarted room {room_num}")

                    # Notify all players in the room to return to lobby
                    for p in room_members[room_num]:
                        try:
                            p["conn"].send("Restart".encode())
                        except:
                            continue

                    # Reset game state values
                    for m in room_members[room_num]:
                        m["game"] = {"x": 0, "y": 0, "rot": 0.0}
                        m["lobby"]["ready"] = False

                    # Reset room tracking
                    room_states[room_num]["default_initialized"] = False
                    ready_players[room_num] = set()
                    ready_next_index[room_num] = 0
                    early_ready[room_num] = set()

        except Exception as e:
            print("Error:", e)
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))