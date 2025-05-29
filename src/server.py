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
pos = ["0:50,50", "1:100,100"] # first game of multi
def threaded_client(conn):
    global room_list, pos
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
                data = reply.split(":")[0]
                if data == "Game Room":
                    reply = json.dumps(room_list)
                if data == "Create Room":
                    room_list.append(f"{room_list.__len__()+1}: {reply.split(":")[1]}")
                    reply = json.dumps(room_list)
                #if data == "Join Room":
                    

            conn.sendall(reply.encode())
        except:
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))