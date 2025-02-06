#!/bin/bash
#!/bin/bash

check_output_expected() {
    local test_type="$1"
    local expected="$2"
    declare received="$3"

    echo "$test_type"
    echo "Expected output: $expected"

    if [[ "$expected" == "$received" ]]; then
        echo -e "---PASS---\n"
    else
        echo "---FAIL---"
        echo -e "Received output: $received\n"
      fi
}

# server response testing 
# - begin server in another terminal 
# - config file set to port: 8002 and userDatabase: ./ticTacToeUsers.json
# LOGIN 
echo -e "----- LOGIN TESTING -----\n"

test_type="correct-login"
expected="LOGIN:ACKSTATUS:0"
output=$(echo "LOGIN:user:password" | ncat localhost 8002)
check_output_expected $test_type $expected $output


test_type="incorrect-username"
expected="LOGIN:ACKSTATUS:1"
output=$(echo "LOGIN:non existent user:password" | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="incorrect-password"
expected="LOGIN:ACKSTATUS:2"
output=$(echo "LOGIN:user:non_existent_password" | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="incorrect-format"
expected="LOGIN:ACKSTATUS:3"
output=$(echo "LOGIN:user" | ncat localhost 8002)
check_output_expected $test_type $expected $output

# REGISTER - cannot test making an account, without actually creating one
echo -e "----- REGISTER  TESTING -----\n"

test_type="user-exists"
expected="REGISTER:ACKSTATUS:1"
output=$(echo "REGISTER:user:password" | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="incorrect-format"
expected="REGISTER:ACKSTATUS:2"
output=$(echo "REGISTER:user" | ncat localhost 8002)
check_output_expected $test_type $expected $output

# BADAUTH
echo -e "----- BADAUTH TESTING -----\n"

test_type="roomlist"
expected="BADAUTH"
output=$(echo "ROOMLIST:VIEWER" | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="create"
expected="BADAUTH"
output=$(echo "CREATE:room" | ncat localhost 8002)
check_output_expected $test_type $expected $output

# ROOMLIST
echo -e "----- ROOMLIST TESTING -----\n"

test_type="no-rooms"
expected="LOGIN:ACKSTATUS:0ROOMLIST:ACKSTATUS:0:"
output=$( (
echo "LOGIN:user:password"
sleep 0.2
echo "ROOMLIST:VIEWER"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="invalid-format"
expected="LOGIN:ACKSTATUS:0ROOMLIST:ACKSTATUS:1"
output=$( (
echo "LOGIN:user:password"
sleep 0.2
echo "ROOMLIST"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

# the following individual sections will be only the failing cases
# reasons explained in the test report along with other testing not found here

# CREATE 
echo -e "----- CREATE TESTING -----\n"

test_type="invalid-name"
expected="LOGIN:ACKSTATUS:0CREATE:ACKSTATUS:1"
output=$( (
echo "LOGIN:user:password"
sleep 0.2
echo "CREATE:** room **"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="incorrect-format"
expected="LOGIN:ACKSTATUS:0CREATE:ACKSTATUS:4"
output=$( (
echo "LOGIN:user:password"
sleep 0.2 
echo "CREATE"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

# JOIN
echo -e "----- JOIN TESTING -----\n"

test_type="no-rooms-exist"
expected="LOGIN:ACKSTATUS:0JOIN:ACKSTATUS:1"
output=$( (
echo "LOGIN:user:password"
sleep 0.2 
echo "JOIN:room:PLAYER"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="incorrect-format"
expected="LOGIN:ACKSTATUS:0JOIN:ACKSTATUS:3"
output=$( (
echo "LOGIN:user:password"
sleep 0.2 
echo "JOIN:room"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

# PLACE

# FORFEIT

# NOROOM
echo -e "----- NOROOM TESTING -----\n"

test_type="place-test"
expected="LOGIN:ACKSTATUS:0NOROOM"
output=$( (
echo "LOGIN:user:password"
sleep 0.2 
echo "PLACE:0:0"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

test_type="forfeit-test"
expected="LOGIN:ACKSTATUS:0NOROOM"
output=$( (
echo "LOGIN:user:password"
sleep 0.2 
echo "FORFEIT"
) | ncat localhost 8002)
check_output_expected $test_type $expected $output

# server to client testing
# LOGIN

# REGISTER

# BADAUTH

# ROOMLIST

# CREATE

# JOIN

# BEGIN

# INPROGRESS

# BOARDSTATUS

# PLACE

# FORFEIT

# GAMEEND

# NOROOM



# skipped functionalities - try and shorten list later

# client to server
# registering new user - do not want to create on each time
# create - success and 256 room limit
# join - success and already existing room
# the rest

# server to client
