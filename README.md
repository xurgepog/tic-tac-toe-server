# Tic-Tac-Toe Server

## Overview

The project features the ability to set up a Tic-Tac-Toe server, allowing yourself or others to join, create rooms, and play games.

This project was created as part of one of my University of Sydney courses. If something seems like a pointless addition, it was most likely a specification to explore a certain concept we had learned.

I plan to refine this project soon, with the main goal of making the server more presentable and tracking the number of wins each player has.

## More Depth

The server and each client must be run in separate windows. This allows the person running the server to play with others or even against themselves using multiple windows. To see how to set this up, see [How to Set Up](#how-to-set-up).

Once the server is set up, it no longer needs to be touched and will only shut down when the user inputs `CTRL + C`. The server will provide useful information to the terminal, such as which clients have joined, what commands they input, and what rooms exist. See [Setting Up the Server](#server).

Clients can enter a variety of commands listed in the [Client Commands](#client-commands) section. These commands allow users to log in and create or join Tic-Tac-Toe games. More details are provided in the introduction to [Client Commands](#client-commands).

## Insight Into the Backend

The project uses Python’s `socket` and `threading` standard libraries for communication between clients and the server. TCP was chosen as the transmission method for the socket. The `threading` library allows multiple people to connect at once without blocking the I/O.

The third-party library `bcrypt` was used to hash the passwords of users registering.

## How to Set Up

### Server

Locate the `config.json` file and change the port number to any available port above `1024`. I used `8002` for testing.

If no changes are made to file names, use `config.json` as `<server config path>`.

Now, input the following command:

`python server.py <server config path>`

If the terminal has blocked I/O, it has worked! The server will now wait for clients to join. If it is working correctly, it will output received commands along with any created room data.

### Client

First, set up the server. Then, run the following command:

`python client.py <server address> <port>`

The port must match the port used in the server's `config.json` file.

To check if the client is connected, see if the server outputs anything.

## Client Commands

Once the client program is running, a variety of commands can be entered. All possible commands are listed below.

The main flow is: **register (if first time) → login → check room list → create or join a room → play using the PLACE command.**

Each room allows two players, but spectators can join games that have already begun. This is why different room lists exist—since the joining options differ between players and spectators. You can also join a room as a spectator before it starts.

### Login To Server:

The first step every time is logging in, unless it is your first time, in which case you [should register an account](#register-account).

Use the following command to log in:

`LOGIN`

You will then be prompted for your username and password.

Currently, logging in serves no real purpose, but I plan to add a score-saving system or other features that make use of authentication.

### Register Account:

You only need to register your account once, but nothing stops you from creating multiple accounts.

Your data will be stored in `ticTacToeUsers.json`. Note that your password will be hashed, but since account creation is easy, avoid using any important passwords.

To delete an old account, open `ticTacToeUsers.json` and remove the corresponding JSON object.

You cannot register an account with a name that already exists.

To register, use the following command:

`REGISTER`

You will then be prompted to enter a username and password.

### View Room List:

The room list displays all current rooms that are joinable as either a player or a spectator.

To access the room list, enter:

`ROOMLIST`

You will then be prompted to choose a mode: `player` or `viewer`.

* **Viewers** can join any room.
* **Players** can only join rooms with one client in them.

### Create A Room:

Creating a room adds it to the room list, and the client will wait for another person to join.

To create a room, enter:

`CREATE`

You will then be prompted to enter a name for your room. If the name already exists, you must try again. To see existing rooms, use the [room List](#view-room-list) command.

**Note:** The person who creates the room will always be X and go first.

### Join A Room:

To join a room, enter:

`JOIN`

You will then be prompted for:

* The mode (`player` or `viewer`).
* The name of the room you want to join.
Use the [room List](#view-room-list) command to see available rooms for your chosen mode.

### Take Your Turn:

Once in the game, you can either take your turn or forfeit.
When choosing a column and row, note that it is 0-indexed.

To take your turn, input:

`PLACE`

You will then be prompted to enter the column and row where you wish to place your X or O.

The **room creator is always X and plays first.**

You can continue placing moves until the game ends, after which you will be able to enter other commands again.

### Forfeit Game:

This will end the game early and declare the opposing player the winner.
This option is only available in-game.

To forfeit, enter:

`FORFEIT`

After forfeiting, you will be able to enter other commands again (except `PLACE`).

Disconnecting early also counts as a forfeit.

### Quit Server

To quit as a client, enter:

`QUIT`

## Credit
This project was created as part of my University of Sydney course.
The `game.py` code was provided to us, and we were allowed to modify and use it as we wished.
The `game.py` you see here is an altered version of the original.