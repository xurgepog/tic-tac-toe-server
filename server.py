# imports
import sys
import os
import json
import socket
import threading
import re
import bcrypt
import game

# constants and globals
MAX_MSG_SZ = 8192
user_database = "" # will update to databse of registered users
online_users = {} # key - client_socket : values - username, room, type
rooms = {} # key - room name : values - players, p_sockets, viewers, v_sockets, 
           # game state, board_status, turn, game_begun
escp_gm_msg = ""

"""
All of the following functions use one or more of these args

Args:
    client_socket (socket.socket): The socket object for connecting to the server
    msg_type (str): The keyword for that message type (e.g. LOGIN, PLACE)
"""
def exit_server(client_socket: socket.socket, msg_recv: str) -> None:
    """
    Raises OS error to handle the client disconnecting - ends their thread
    """
    raise OSError

def noroom_check(client_socket: socket.socket) -> bool:
    """
    Checks if client is not in a room

    Returns:
        True if not in a room, else false
    """
    if online_users[client_socket]["room"] == "":
        client_socket.sendall("NOROOM".encode())
        return True
    return False

def read_json(filename: str) -> dict:
    """
    Reads requested json file

    Returns:
        json file as dictionary
    """
    with open(filename, 'r') as f:
        return json.load(f)

def write_json(filename: str, dictionary: dict) -> None:
    """
    Writes over the requested json file, using given dictoinary
    """
    with open(filename, 'w') as f:
        json.dump(dictionary, f, indent=4)

def find_user(username: str) -> str:
    """
    Looks for username in database

    Returns:
        password if found, else empty string
    """
    user_data = read_json(user_database)
    for user in user_data:
        if user["username"] == username:
            return user["password"]
    return ""

def login(client_socket: socket.socket, msg_recv: str) -> None:
    """
    Interprets clients login message, does requested action if possible, then sends
    acknowledgement of action, or why it was not possible
    """
    msg = msg_recv[0] + ":ACKSTATUS:"

    password = find_user(msg_recv[1])
    # incorrect arguments
    if len(msg_recv) != 3:
        status_info = '3'
    # user found
    elif password:
        # correct password
        if bcrypt.checkpw(msg_recv[2].encode(), password.encode()):
            online_users[client_socket] = {
                "username": msg_recv[1],
                "room": "",
                "type": ""
            }
            status_info = '0'
        # incorrect password
        else:
            status_info = '2'
    # no user found
    else:
        status_info = '1'

    client_socket.sendall((msg + status_info).encode())

def register(client_socket: socket.socket, msg_recv: str) -> None:
    """
    Interprets clients register message, does requested action if possible, then sends
    acknowledgement of action, or why it was not possible
    """
    msg = msg_recv[0] + ":ACKSTATUS:"

    # incorrect arguments
    if len(msg_recv) != 3:
        status_info = '2'
    # username already exists
    elif find_user(msg_recv[1]):
        status_info = '1'
    # add to database
    else:
        user_data = read_json(user_database)

        hashed_pw = bcrypt.hashpw(msg_recv[2].encode(), bcrypt.gensalt())
        new_user = {
            "username": msg_recv[1],
            "password": hashed_pw.decode()
        }

        user_data.append(new_user)
        write_json(user_database, user_data)
        status_info = '0'

    client_socket.sendall((msg + status_info).encode())

def badauth_check(client_socket: socket.socket) -> bool:
    """
    Checks if client has logged in
   
    Returns:
        True if client has logged in, else false
    """
    if client_socket not in online_users:
        client_socket.sendall("BADAUTH".encode())
        return True
    return False

def create(client_socket: socket.socket, msg_recv: str) -> None:
    """
    Interprets clients create message, does requested action if possible, then sends
    acknowledgement of action, or why it was not possible
    """
    if badauth_check(client_socket):
        return

    msg = msg_recv[0] + ":ACKSTATUS:"

    # if invalid format
    if len(msg_recv) != 2:
        status_info = '4'
    # if too many rooms
    elif len(rooms) >= 256:
        status_info = '3'
    # if room name already exists
    elif msg_recv[1] in rooms:
        status_info = '2'
    # if name valid
    elif bool(re.match("^[a-zA-Z0-9 _-]+$", msg_recv[1])):
        rooms[msg_recv[1]] = {
            "players": [online_users[client_socket]["username"]],
            "p_sockets": [client_socket],
            "viewers": [],
            "v_sockets": [],
            "game_state": '',
            "board_status": "000000000",
            "turn": 0,
            "game_begun": False
        }
        online_users[client_socket]["room"] = msg_recv[1]
        online_users[client_socket]["type"] = "P1"
        status_info = '0'
    # if invalid
    else:
        status_info = '1'

    client_socket.sendall((msg + status_info).encode())
    if status_info == '0':
        begin(client_socket, msg_recv[1])

def get_player_rooms() -> str:
    """
    Finds all the rooms that are joinable as a player

    Returns:
        string of all player joinable room names seperated by commas
    """
    rooms_list = ""
    for room in rooms:
        if len(rooms[room]["players"]) == 1:
            rooms_list += room + ','
    return rooms_list[:-1]

def get_viewer_rooms() -> str:
    """
    Finds all the rooms that are joinable as a viewer

    Returns:
        string of all viewer joinable room names seperated by commas
    """
    rooms_list = ""
    for room in rooms:
        rooms_list += room + ','
    return rooms_list[:-1]

def roomlist(client_socket: socket.socket, msg_recv: str) -> None:
    """
    Interprets clients roomlist message, does requested action if possible, then sends
    acknowledgement of action, or why it was not possible
    """
    if badauth_check(client_socket):
        return

    msg = msg_recv[0] + ":ACKSTATUS:"
    # incorrect arguments
    if len(msg_recv) != 2:
        status_info = '1'
    elif msg_recv[1] == "PLAYER":
        rooms_list = get_player_rooms()
        status_info = "0:" + rooms_list
    elif msg_recv[1] == "VIEWER":
        rooms_list = get_viewer_rooms()
        status_info = "0:" + rooms_list
    # if non-existent mode was entered
    else:
        status_info = '1'

    client_socket.sendall((msg + status_info).encode())

def join(client_socket: socket.socket, msg_recv: str) -> None:
    """
    Interprets clients join message, does requested action if possible, then sends
    acknowledgement of action, or why it was not possible
    """
    if badauth_check(client_socket):
        return

    msg = msg_recv[0] + ":ACKSTATUS:"

    rooms_list_player = get_player_rooms().split(',')
    rooms_list_viewer = get_viewer_rooms().split(',')
    # incorrect arguments
    if len(msg_recv) != 3:
        status_info = '3'
    elif msg_recv[2] == "PLAYER":
        # if joinable room - player
        if msg_recv[1] in rooms_list_player:
            rooms[msg_recv[1]]["players"].append(online_users[client_socket]["username"])
            rooms[msg_recv[1]]["p_sockets"].append(client_socket)
            online_users[client_socket]["room"] = msg_recv[1]
            online_users[client_socket]["type"] = "P2"
            status_info = '0'
        # if room full
        elif msg_recv[1] in rooms_list_viewer:
            status_info = '2'
        # if room not found - player
        else:
            status_info = '1'
    elif msg_recv[2] == "VIEWER":
        # if joinable room - viewer
        if msg_recv[1] in rooms_list_viewer: # kind of repetitive
            rooms[msg_recv[1]]["viewers"].append(online_users[client_socket]["username"])
            rooms[msg_recv[1]]["v_sockets"].append(client_socket)
            online_users[client_socket]["room"] = msg_recv[1]
            online_users[client_socket]["type"] = msg_recv[2]
            status_info = '0'
        # if room not found - viewer
        else:
            status_info = '1'
    # if non-existent mode was entered
    else:
        status_info = '3'

    client_socket.sendall((msg + status_info + '\n').encode())

    # send begin message to room users
    if status_info == '0':
        if msg_recv[2] == "PLAYER":
            msg_type = "BEGIN"
        else:
            msg_type = "INPROGRESS"

        player1 = rooms[msg_recv[1]]["players"][0]
        player2 = rooms[msg_recv[1]]["players"][1]
        msg = msg_type + ':' + player1 + ':' + player2

        if msg_type == "BEGIN":
            for socket in rooms[msg_recv[1]]["p_sockets"]:
                socket.sendall(msg.encode())
            for socket in rooms[msg_recv[1]]["v_sockets"]:
                socket.sendall(msg.encode())
        elif msg_type == "INPROGRESS":
            client_socket.sendall(msg.encode())
        begin(client_socket, msg_recv[1])

def begin(client_socket: socket.socket, room_name: str) -> None:
    """
    Handles in room client commands, receiving client data, converting into requested move,
    then storing for other threads in same room to use
    Upon updated board, sends appropriate message with new board state to all clients in room
    
    Args:
        room_name (str): holds name of room that is being handled
    """
    # if board not created, create it
    if not rooms[room_name]["game_state"]:
        rooms[room_name]["game_state"] = game.create_board()
    players = [game.CROSS, game.NOUGHT]
    
    # when second player joins allow first player move
    if len(rooms[room_name]["players"]) == 2:
        rooms[room_name]["game_begun"] = True

    status_code = ''
    board_status = ''
    try:
        while not status_code:
            player_move = client_socket.recv(MAX_MSG_SZ).decode().strip().split(':')

            # if game is over use this input as out of game input
            if room_name not in rooms:
                global escp_gm_msg
                escp_gm_msg = player_move
                break

            # hold move if game not begun
            while rooms[room_name]["game_begun"] == False:
                continue

            # hold move if not turn
            while rooms[room_name]["p_sockets"][rooms[room_name]["turn"] % 2] != client_socket:
                continue

            # update boardstatus and game state according to player move
            if player_move[0] == "PLACE":
                board = rooms[room_name]["game_state"]
                board_status = rooms[room_name]["board_status"]
                turn = rooms[room_name]["turn"]

                player = players[turn % 2]
                col = int(player_move[1])
                row = int(player_move[2])
                position = game.player_turn(player, board, col, row)

                board_status = list(board_status)
                board_status[3 * row + col] = str(turn % 2 + 1)
                board_status = ''.join(board_status)

                rooms[room_name]["game_state"] = board
                rooms[room_name]["board_status"] = board_status

                # check if the game is over
                if game.player_wins(player, board):
                    msg_type = "GAMEEND"
                    status_code = '0'
                elif game.players_draw(board):
                    msg_type = "GAMEEND"
                    status_code = '1'
                else:
                    player = game.NOUGHT if player == game.CROSS else game.CROSS
                    msg_type = "BOARDSTATUS"

            elif player_move[0] == "FORFEIT":
                board_status = rooms[room_name]["board_status"]
                msg_type = "GAMEEND"
                status_code = '2'

            elif player_move[0] == "":
                raise OSError

            # construct message to send
            msg = msg_type + ':'  + board_status
            if status_code:
                rooms[room_name]["game_begun"] = False
                turn = rooms[room_name]["turn"]
                msg += ':' + status_code
                if status_code == '0':
                    msg += ':' + rooms[room_name]["players"][turn % 2]
                elif status_code == '2':
                    msg += ':' + rooms[room_name]["players"][(turn + 1) % 2]

            for socket in rooms[room_name]["p_sockets"]:
                socket.sendall(msg.encode())
            for socket in rooms[room_name]["v_sockets"]:
                socket.sendall(msg.encode())

            rooms[room_name]["turn"] = turn + 1

            if msg_type == "GAMEEND":
                rooms.pop(room_name, None)

    except OSError:
        print("Client disconnected")

        # send to everyone else forfeit
        if client_socket in rooms[room_name]["p_sockets"]:
            winner_index = (rooms[room_name]["p_sockets"].index(client_socket) + 1) % 2
            msg = "GAMEEND:" + rooms[room_name]["board_status"] + ":2:" + \
rooms[room_name]["players"][winner_index]

            for socket in rooms[room_name]["p_sockets"]:
                if socket != client_socket:
                    socket.sendall(msg.encode())
            for socket in rooms[room_name]["v_sockets"]:
                socket.sendall(msg.encode())
        # if viewer disconnected
        elif client_socket in rooms[room_name]["v_sockets"]:
            v_index = rooms[room_name]["v_sockets"].index(client_socket)
            rooms[room_name]["v_sockets"][v_index]
            rooms[room_name]["viewers"][v_index]

        rooms.pop(room_name, None)

def handle_client(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    """
    Get client messages and runs appropriate function in order to interpret data and
    send back appropriate message
    Does not handle in room functions

    Args:
        client_address (tuple[str, int]): holds [0] ip of client [1] port of client
    """
    msg_to_func = {
        "": exit_server,
        "LOGIN": login,
        "REGISTER": register,
        "CREATE": create,
        "ROOMLIST": roomlist,
        "JOIN": join
    }

    # While client connected
    print(f"Client connected: {client_address}")
    client_connected = True

    while client_connected:
        try:
            # Recieve message and run appropriate function
            global escp_gm_msg
            if escp_gm_msg:
                msg_recv = escp_gm_msg
                escp_gm_msg = ""
            else:
                msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split(':')
            print(f"Received data: {msg_recv}")

            # make in room commands not accessible
            if msg_recv[0] == "PLACE" or msg_recv[0] == "FORFEIT":
                if not badauth_check(client_socket):
                    client_socket.sendall("NOROOM".encode())
            else:
                msg_to_func[msg_recv[0]](client_socket, msg_recv)
            print(rooms)

        except OSError:
            client_connected = False
            if client_socket in online_users:
                del online_users[client_socket]
            client_socket.close()
            print(f"Client disconnected: {client_address}")

def main(args: list[str]) -> None:
    """
    Sets up server, gets user socket then creates thread for handling client messages

    Args:
        args (list[str]): holds [0] server config path
    """
    config = read_json(args[0])
    port = config["port"]
    global user_database
    user_database = os.path.expanduser(config["userDatabase"])

    # Setting up server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("", port))
    server_socket.listen(5)

    # Waiting for a client connection
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

        # If waiting for client and ctrl c - quit cleanly
        except KeyboardInterrupt:
            print("\nClosing server...")
            server_socket.close()
            sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
