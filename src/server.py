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
start_room = {}

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
                "respawn": m["game"]["res"],
                "penetration": m["game"]["pen"],
                "time_freeze": m["game"]["tf"]
            }
            for m in room_members[room_num]
        ]

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
        for m in room_members[room_num]:
            try:
                m["conn"].send(message.encode())
            except:
                pass

def threaded_client(conn):
    global room_list, room_members, full_room_list, room_states, ready_players, ready_next_index, early_ready, start_room

    while True:
        try:
            data = conn.recv(2048).decode("utf-8")
            if not data:
                break
            #print("Received:", data)
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
                    "game": {"x": 0, "y": 0, "rot": 0.0, "res": False, "pen": False, "tf": False}
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
                        "game": {"x": 0, "y": 0, "rot": 0.0, "res": False, "pen": False, "tf": False}
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
                    # Remove based on connection only
                    room_members[room_num] = [m for m in room_members[room_num] if m["conn"] != conn]

                    # Separate host and non-hosts
                    host = None
                    others = []

                    for m in room_members[room_num]:
                        if m["player_id"] == 0:
                            host = m
                        else:
                            others.append(m)

                    # Reassign player IDs for non-hosts starting from 1
                    for i, m in enumerate(others, start=1):
                        m["player_id"] = i
                        try:
                            m["conn"].sendall(f"UpdateID:{i}\n".encode())
                        except:
                            pass

                    # Rebuild room_members list
                    room_members[room_num] = ([host] if host else []) + others

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

            elif command == "Kick":
                room_num, target_id = parts[1], int(parts[2])

                if room_num in room_members:
                    kicked_conn = None

                    # Remove the target player and store their connection
                    new_room = []
                    for m in room_members[room_num]:
                        if m["player_id"] == target_id:
                            kicked_conn = m["conn"]
                            try:
                                kicked_conn.send("Kicked\n".encode())
                            except:
                                pass
                        else:
                            new_room.append(m)
                    
                    room_members[room_num] = new_room

                    # Separate host and others
                    host = None
                    others = []
                    for m in room_members[room_num]:
                        if m["player_id"] == 0:
                            host = m
                        else:
                            others.append(m)

                    # Reassign IDs for non-hosts starting from 1
                    for i, m in enumerate(others, start=1):
                        old_id = m["player_id"]
                        m["player_id"] = i
                        try:
                            m["conn"].sendall(f"UpdateID:{i}\n".encode())
                        except:
                            pass

                    # Rebuild room member list
                    room_members[room_num] = ([host] if host else []) + others

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

                    broadcast_lobby_update(room_num)

            elif command == "Update":
                room_num, pid, name, skin_id, ready_str = parts[1], int(parts[2]), parts[3], int(parts[4]), parts[5]
                ready = ready_str == "True"

                # Update the matching player in the room based on connection (safe from player_id shifts)
                for m in room_members.get(room_num, []):
                    if m["conn"] == conn:
                        m["name"] = name
                        m["skin_id"] = skin_id
                        m["lobby"]["ready"] = ready
                        break

                # Broadcast updated lobby state to all clients
                broadcast_lobby_update(room_num)
            
            elif command == "Start":
                # Save the room string from room_list before removing
                for r in room_list:
                    if room_num in r:
                        start_room[room_num] = r
                        break

                # Remove the room from room_list
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
                respawn_str = parts[5]
                penetration_str = parts[6]
                time_freeze_str = parts[7]
                # After countdown, handle actual player game data
                x = float(parts[2])
                y = float(parts[3])
                rot = float(parts[4])
                respawn = respawn_str == "True"
                penetration = penetration_str == "True"
                time_freeze = time_freeze_str == "True"

                for m in room_members[room_num]:
                    if m["player_id"] == player_id:
                        m["game"]["x"] = x
                        m["game"]["y"] = y
                        m["game"]["rot"] = rot
                        m["game"]["res"] = respawn
                        m["game"]["pen"] = penetration
                        m["game"]["tf"] = time_freeze
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

                    # Restore room string if it’s not in either list
                    if (room_num not in "".join(room_list)) and (room_num not in "".join(full_room_list)):
                        if room_num in start_room:
                            room_list.append(start_room[room_num])
                            print(f"[INFO] Room {room_num} re-added to room_list after restart.")
                    
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

                    # Reset room tracking
                    room_states[room_num]["default_initialized"] = False
                    ready_players[room_num] = set()
                    ready_next_index[room_num] = 0
                    early_ready[room_num] = set()
                    
            elif command == "UseFreeze":
                room_num, user_id = parts[1], int(parts[2])
                print(f"DEBUG SERVER: Player {user_id} used freeze in room {room_num}")
                
                if room_num in room_members:
                    # Find the player with the highest X coordinate (furthest ahead)
                    highest_x = -999999
                    target_player = None
                    
                    for member in room_members[room_num]:
                        player_id = member["player_id"]
                        player_x = member["game"]["x"]
                        
                        # Don't target the player who used the skill
                        if player_id != user_id:
                            if player_x > highest_x:
                                highest_x = player_x
                                target_player = member
                    
                    if target_player:
                        target_id = target_player["player_id"]
                        try:
                            # Send freeze command only to the player with highest X
                            target_player["conn"].send(f"GetFrozen:{user_id}".encode())
                            print(f"DEBUG SERVER: Player {user_id} froze player {target_id} (highest X: {highest_x})")
                        except Exception as e:
                            print(f"Failed to send freeze to player {target_id}: {e}")
                    else:
                        print(f"DEBUG SERVER: No valid target found for freeze from player {user_id}")
                
            # ADD after "UseFreeze" command handling:
            elif command == "UseTeleport":
                room_num, user_id = parts[1], int(parts[2])
                print(f"DEBUG SERVER: Player {user_id} used teleport in room {room_num}")
                    
                if room_num in room_members:
                    # Find highest X player and user player
                    highest_x = -999999
                    target_player = None
                    user_player = None
                        
                    for member in room_members[room_num]:
                        player_id = member["player_id"]
                        player_x = member["game"]["x"]
                            
                        if player_id == user_id:
                            user_player = member
                        elif player_x > highest_x:
                            highest_x = player_x
                            target_player = member
                        
                    if target_player and user_player:
                        # Swap positions
                        user_x = user_player["game"]["x"]
                        user_y = user_player["game"]["y"]
                        target_x = target_player["game"]["x"]
                        target_y = target_player["game"]["y"]
                        target_id = target_player["player_id"]
                        
                        user_player["game"]["x"] = target_x
                        user_player["game"]["y"] = target_y
                        target_player["game"]["x"] = user_x
                        target_player["game"]["y"] = user_y
                        
                        # Send teleport commands
                        try:
                            user_player["conn"].send(f"TeleportTo:{target_x}:{target_y}".encode())
                            target_player["conn"].send(f"TeleportTo:{user_x}:{user_y}".encode())
                            print(f"DEBUG SERVER: Teleport swap completed between {user_id} and {target_id}")
                        except Exception as e:
                            print(f"Failed to send teleport commands: {e}")
        except Exception as e:
            print("Error:", e)
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(threaded_client, (conn,))