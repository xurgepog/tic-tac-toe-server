# imports
import sys
import socket

# constants and globals
MAX_MSG_SZ = 8192 # max size in bytes of mesg received
user = "" # holds the users name once logged in

"""
All of the following functions use one or more of these args

Args:
    client_socket (socket.socket): The socket object for connecting to the server  
    msg_type (str): The keyword for that message type (e.g. LOGIN, PLACE)
"""
def exit_server(client_socket: socket.socket, msg_type: str) -> None:
    """
    Closes server socket and exits program
    """
    print("Exiting")
    client_socket.close()
    sys.exit(0)

def badauth() -> None:
    """
    Prints badauth error message - user not logged in for auth required command
    """
    print("Error: You must be logged in to perform this action", file=sys.stderr)

def noroom() -> None:
    """
    Prints noroom error message - user not in room for inroom required command
    """
    print("Error: You must be in a room to perform this action", file=sys.stderr)

def user_data_request(client_socket: socket.socket, msg_type: str) -> str:
    """
    Handles creating messages that require aquiring the user's username and password

    Returns:
        username
    """
    username = input("Enter username: ")
    password = ""
    # Ensuring password can't be empty
    while not password:
        password = input("Enter password: ")
        if not password:
            print("Error: Password can not be empty", file=sys.stderr)

    msg = msg_type + ':' + username + ':' + password
    client_socket.sendall(msg.encode())
    return username

def login(client_socket: socket.socket, msg_type: str) -> None:
    """
    Creates login message to send to the server, then handles server response  
    """
    username = user_data_request(client_socket, msg_type)
    msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split(':')

    if msg_recv[2] == '0':
        global user
        user = username
        print(f"Welcome {username}")
    elif msg_recv[2] == '1':
        print(f"Error: User {username} not found", file=sys.stderr)
    elif msg_recv[2] == '2':
        print(f"Error: Wrong password for user {username}", file=sys.stderr)

def register(client_socket: socket.socket, msg_type: str) -> None:
    """
    Creates register message to send to the server, then handles server response  
    """
    username = user_data_request(client_socket, msg_type)

    msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split(':')

    if msg_recv[2] == '0':
        print(f"Successfully created user account {username}")
    elif msg_recv[2] == '1':
        print(f"Error: User {username} already exists", file=sys.stderr)

def create(client_socket: socket.socket, msg_type: str) -> None:
    """
    Creates create message to send to the server, then handles server response  
    """
    room_name = input("Enter room name you want to create: ")
    msg = msg_type + ':' + room_name

    client_socket.sendall(msg.encode())
    msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split(':')

    if msg_recv[0] == "BADAUTH":
        badauth()
        return

    if msg_recv[2] == '0':
        print(f"Successfully created room {room_name}")
        print("Waiting for second player")
        begin(client_socket, '')
    elif msg_recv[2] == '1':
        print(f"Error: Room {room_name} is invalid", file=sys.stderr)
    elif msg_recv[2] == '2':
        print(f"Error: Room {room_name} already exists", file=sys.stderr)
    elif msg_recv[2] == '3':
        print("Error: Server already contains a maximum of 256 rooms", file=sys.stderr)

def get_mode() -> str:
    """
    Handles creating messages that require the user inputting the mode (player/viewer)

    Returns:
        valid mode
    """
    correct_mode = False
    while not correct_mode:
        mode = input("Do you want to have a room list as player or viewer? (Player/Viewer) ")
        mode = mode.upper() # put in line above? but too long
        if mode in ("PLAYER", "VIEWER"):
            correct_mode = True
        else:
            print("Unknown input.")
    return mode

def roomlist(client_socket: socket.socket, msg_type: str) -> None:
    """ 
    Creates roomlist message to send to the server, then handles server response
    """
    # ensuring correct input
    mode = get_mode()
    msg = msg_type + ':' + mode

    client_socket.sendall(msg.encode())
    msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split(':')

    if msg_recv[0] == "BADAUTH":
        badauth()
        return

    if msg_recv[2] == '0':
        print(f"Room available to join as {mode}: {msg_recv[3]}")
    elif msg_recv[2] == '1':
        print("Error: Please input a valid mode.", file=sys.stderr)

def join(client_socket: socket.socket, msg_type: str) -> None:
    """
    Creates join message to send to the server, then handles server response
    """
    room_name = input("Enter room name you want to join: ")
    mode = get_mode()

    msg = msg_type + ':' + room_name + ':' + mode

    client_socket.sendall(msg.encode())
    msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split('\n')

    # in case both messages are sent to client in quick succession
    begin_msg = ''
    if len(msg_recv) > 1:
        begin_msg = msg_recv[1]
    msg_recv = msg_recv[0].split(':')

    if msg_recv[0] == "BADAUTH":
        badauth()
        return

    if msg_recv[2] == '0':
        print(f"Successfully joined room {room_name} as a {mode}")
        begin(client_socket, begin_msg)
    elif msg_recv[2] == '1':
        print(f"Error: No room named {room_name}", file=sys.stderr)
    elif msg_recv[2] == '2':
        print(f"Error: The room {room_name} already has 2 players")

def col_row_check(axis_name: str) -> str:
    """
    Get valid col or row input

    Args:
        axis_name (str): the name of the axis being inputted (col/row)

    Returns:
        valid axis input as string
    """
    axis = -1
    while axis < 0 or axis > 2:
        axis = input(axis_name + ": ")
        try:
            axis = int(axis)
            if axis < 0 or axis > 2:
                raise Exception
        except Exception:
            print(axis_name + " values must be an integer between 0 and 2")
            axis = -1
    return str(axis)

"""
The following function use the following arg

Args:
    board (str): holds 0s, 1s or 2s for blank spot X and O respectively for each space
                 on the board from left to right, top to bottom
"""
def place(client_socket: socket.socket, msg_type: str, board: str) -> str:
    """
    Gets valid position for player's move and sends to server

    Returns:
        message recieved from server in response
    """
    valid_space = False
    markers = [' ', 'X', 'O']
    while not valid_space:
        col = col_row_check("Column")
        row = col_row_check("Row")
        spot_val = board[3  * int(row) + int(col)]
        if spot_val == '0':
            valid_space = True
        else:
            print(f"({col}, {row}) is occupied by {markers[int(spot_val)]}")

    msg = msg_type + ':' + col + ':' + row

    client_socket.sendall(msg.encode())
    msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split('\n')
    return msg_recv

def forfeit(client_socket: socket.socket, msg_type: str, board: str) -> str:
    """
    Sends forfeit message

    Returns:
        Message recieved from server in response
    """
    client_socket.sendall(msg_type.encode())
    msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split('\n')
    return msg_recv

def print_board(board: str) -> None:
    """
    Prints out board recieved so user can easily see current game state
    """
    num_to_sym = {
        '0': ' ',
        '1': 'X',
        '2': 'O'
        }

    for index, num in enumerate(board):
        if index % 3 == 0:
            print("\n-------------")
            print("|", end=' ')

        print(num_to_sym[num], end= ' | ')
    print("\n-------------\n")

def begin(client_socket: socket.socket, begin_msg: str) -> None:
    """
    Handles in room player commands, receiving player input only when it is their turn
    Also handles server sent messages in reponse to player inputs
    """
    msg_to_func = {
        "PLACE": place,
        "FORFEIT": forfeit,
    }
    # handling if begin message was joined with previous
    if not begin_msg:
        msg_recv = client_socket.recv(MAX_MSG_SZ).decode().strip().split(':')
    else:
        msg_recv = begin_msg.strip().split(':')

    # send appropriate message upon joining a room that has now/was begun
    if msg_recv[0] == "BEGIN":
        print(f"Match between {msg_recv[1]} and {msg_recv[2]} will commence, \
it is currently {msg_recv[1]}'s turn")
        board = "000000000"
        print_board(board)
    elif msg_recv[0] == "INPROGRESS":
        print(f"Match between {msg_recv[1]} and {msg_recv[2]} is currently in progress, \
it is {msg_recv[1]}'s turn")

    turn = 0
    double_recv_msg = ""
    while True:
        try:
            # if turn can send message
            if msg_recv[turn % 2 + 1] == user:
                user_msg = input("Your turn:\n")
                if double_recv_msg: # if double status recieved, handle
                    board_status = double_recv_msg
                    double_recv_msg = ""
                else:
                    board_status = msg_to_func[user_msg](client_socket, user_msg, board)
            # if not turn or viewer
            else:
                if user in msg_recv:
                    print("Wait for your turn") # change later
                else:
                    print(f"{msg_recv[turn % 2 + 1]}'s turn")
                if double_recv_msg:
                    board_status = double_recv_msg
                    double_recv_msg = ""
                else:
                    board_status = client_socket.recv(MAX_MSG_SZ).decode().strip().split('\n')

            # handling recieved server message
            if len(board_status) == 2:
                double_recv_msg = board_status[1].split(':')
            board_status = board_status[0].split(':')

            if board_status[0] == "BOARDSTATUS":
                board = board_status[1]
                print_board(board)

            elif board_status[0] == "GAMEEND":
                print_board(board_status[1])
                if board_status[2] == '0':
                    if user == board_status[3]:
                        print("Congratulations, you won!")
                    elif user in msg_recv:
                        print("Sorry you lost. Good luck next time.")
                    else:
                        print(f"{board_status[3]} has won this game")

                elif board_status[2] == '1':
                    print("Game ended in a draw")
                elif board_status[2] == '2':
                    print(f"{board_status[3]} won due to the opposing player forfeiting")
                break
            turn += 1

        # if user enters a non-command
        except KeyError:
            print(f"Unknown command: {user_msg}\nPlease try again")

        # if user enters CTRL + D to exit the server
        except EOFError:
            exit_server(client_socket, "QUIT")

        # if unknown server message received
        except RuntimeError:
            print("Unknown message received from server. Exiting...")
            exit_server(client_socket, "QUIT")

def main(args: list[str]) -> None:
    """
    Get user input and run appropriate function in order to recieve data to send to server
    Does not include in room logic - this logic is in begin()

    Args:
        args (list[str]): holds [0] ip of server [1] server port
    """
    msg_to_func = {
        "QUIT": exit_server,
        "BADAUTH": badauth,
        "LOGIN": login,
        "REGISTER": register,
        "CREATE": create,
        "ROOMLIST": roomlist,
        "JOIN": join
    }

    # set up server connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (args[0], int(args[1]))
    client_socket.connect(server_address)
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    while True:
        try:
            # user input handling
            user_msg = input()
            if user_msg in ("PLACE", "FORFEIT"): # incorrect in room command use
                client_socket.sendall(user_msg.encode())
            else:
                msg_to_func[user_msg](client_socket, user_msg)

        # if user enters a non-command
        except KeyError:
            print(f"Unknown command: {user_msg}\nPlease try again")

        # if user enters CTRL + D to exit the server
        except EOFError:
            exit_server(client_socket, "QUIT")

        # if unknown server message received
        except RuntimeError:
            print("Unknown message received from server. Exiting...")
            exit_server(client_socket, "QUIT")

if __name__ == "__main__":
    main(sys.argv[1:])
