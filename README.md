# Tic-Tac-Toe Server

## Overview

The project features the ability to setup a tic-tac-toe server, then allows yourself or others to join the server, create rooms, and play games of tic-tac-toe.

This project was created as part of one of my University of Sydney courses, so if something seems like a pointless addition, it was most likely a specification to explore a certain thing we had learnt.

I plan to touch up this project a little bit soon, with the main goal to make the server more presentable, and store how many wins each player has.

## More depth

The server and each client is to be run in seperate windows. This way the one running the server is capable of playing with others or even against themselves through the use of multiple windows. To see how to setup this up see here [## How To Setup].

Once the server is setup it no longer needs to be touched, and will only be shut down once the user inputs (whatever CTRL C does). The server will provide useful information to the terminal about which clients have joined, what commands they input, and what rooms exist. See [## How to Setup ### Server].

Clients can enter a variety of commands listed in the [## Client Commands] section. These commands allow the user to login then create / join tic-tac-toe games. More information is provided in the opening paragrah of [## Client Commands].

## Insight Into The Backend

The project makes use python and the socket library to communicate between clients and the server. TCP is used. 

## How to Setup

### Server

Locate the config.json file. Change the port number to whatever port you wish to run the server on within your device. Note that anything over 1024 should be fine, I used 8002 for all my testing.

Now input the following command:

`python3 server.py <server config path>`

If the terminal has blocked IO it has worked! It will then wait for clients to join and if it is working the server will output what commands it recieves, along with any room data that is created.

### Client

First the server must be setup. Now the following command should be run:

`python3 client.py <server address> <port>`

The port given must match the port used in the server running user's config.json file.


## Client Commands

Once the client is has their program running they can enter a variety of commands. All possible commands can be seen below.

The main flow is: register if first time, login, create or join a room, then play through the place command.

Each room allows two players, but viewers can join games that have already begun. This is why different room lists exist, since the options to join are different between player and viewer. You can also join a room as a viewer before it has begun.

### Login To Server:

The first step everytime is logging on, unless its your first time in which you should [### register  account].

The following command is used to log on:

`LOGIN`

You will then be prompted for you username and password.

Currently there is no real reason to logging in, but I plan to add a score saving system or something else that makes use of the logging in system.

### Register Account:

Only need to register your account the first time. Nothing stops you from creating more accounts however.

Your data will be stored in ticTacToeUsers.json. Note that your password will be hashed, however its not worth using any passwords that mean anything to you since it is super easy to make a new account right now and delete the old one.

To delete you old account you just need to open the ticTacToeUsers.json and remove the appropraite JSON object.

You will not be able to register an account if the name already exists however.

To register use the following command:

`REGISTER`

You will then be prompted with entering the username and password you wish to use.

### View Roomlist:

Roomlist shows all of the current rooms that exist and are joinable as either a player or viewer depending on which you enter as the mode.

To access the room list enter the following command:

`ROOMLIST`

You will then be prompted for a mode, which you can input either "player" or "viewer" as a response to. Viewers can join any room, whereas players can only join rooms that have one client in them.

### Create A Room:

Creating a room will add it to the roomlist and will have the client wait for another person to join.

To create a room enter the following command:

`CREATE`

You will then be prompted to enter a name for your room. If it already exists you will have to try again. To see existing rooms use the room list command. See [### Roomilst].

Note the one who creates the room will always be x's and go first.

### Join A Room:

To join a room enter the following command:

`JOIN`

You will then be prompted for what mode you want to join as, enter either "player" or "viewer", as well as the room name you want to join. Use roomlist to see the possible rooms for the mode you want to join a game as. See [### Roomlist].

### Take Your Turn:

Once in the game you can either take your turn or forfeit. When chossing column and row, please note that it is 0 indexed.

To take your turn input the following command:

`PLACE`

You will then be prompted with the column and row you wish to place your x or o.

The one who created the room will always be x's and be first to go.

You can keep on placing until the game is over, where you will be able to enter all the other available commands once again.

### Forfeit Game:

This will end the game early and declare the opposing player the winner. This option is only available in game. If you ever need to quit before someone else joins... don't.

To forfeit enter the following command:

`FORFEIT`

Once you forfeit you will be able to enter all other available commands, besides place, once again

### Quit Server

To quit as a client type the following command:

`QUIT`

## Credit
This project was created as part of my USYD course
The game.py code was given to us, and we were allowed the ability to modify however we wanted.
I have made decent changes to the code given.

## Change Before Final commit
- REMEMBER TO MAKE HARD WRAP ONCE DONE!!!!
- change server messages to be mroe useful to other people