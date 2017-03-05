import socket
import sys
import time
import _thread
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import re
class Server:
    MAX_CLIENTS = 5
    AUTH_MSG = 0
    PASS = "pass"



    def __init__(self, port, key):
        self.port = port
        self.key = key
        self.mode = 0 # Method for encryption (0 = none, 1 = AES128, 2 = AES256)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.backend = default_backend()
        self.alive = True
        try:
            self.socket.bind(('', self.port))
            self.socket.listen(Server.MAX_CLIENTS)
            print("Server opened on port", self.port)
        except:
            print("Error opening socket, close other servers or try another port")

    def initCrypt(self, mode):
        if mode.upper() == "NONE":
            print("Initializing NONE")
            self.mode = 0;
            return 0

        elif mode.upper() == "AES128":
            self.mode = 1;
            print("Initializing AES128")
            aeskey = bytearray(self.key, "UTF-8")
            self.key = bytearray(self.key, "UTF-8")
            while (len(aeskey)) < 128:
                self.aeskey = bytearray(aeskey + self.key)
            aeskey = aeskey[:128]
            return aeskey

        elif mode.upper() == "AES256":
            self.mode = 2;
            print("Initializing AES256")
            aeskey = bytearray(self.key, "UTF-8")
            self.key = bytearray(self.key, "UTF-8")
            while (len(aeskey)) < 256:
                self.aeskey = bytearray(aeskey + self.key)
            aeskey = aeskey[:256]
            return aeskey

        else:
            #Something is wrong
            print("Client desired cipher", mode.decode().strip(),"not available")
            self.alive = False
            return 0

    def close(self, message):
        print(message)
        self.socket.close()
        self.alive = False

    def recieveAndDecrypt(self):
        print("Receive and decrypt")
        toDecrypt = self.connection.recv(1024);
        if(self.mode != 0):
            self.decryptor.update(toDecrypt) + self.decryptor.finalize()
        return toDecrypt

    def encryptAndSend(self, toSend):
        print("Encrypt and send")
        if (self.mode != 0):
            self.encryptor.update(toSend) + self.encryptor.finalize()
        self.connection.send(toSend)
    def sendFile(self, filename):
        print("Sending", filename,  "to client")
        file = open(filename, 'rb')
        l = file.read(1024)
        while(l):
            self.encryptAndSend(l)
            l = file.read(1024)
        print("File finished sending")


    def receiveFile(self, filename):
        print("Receiving", filename)
        file = open(filename, 'wb')
        l = self.recieveAndDecrypt()
        while(l):
            file.write(l)
            l = self.recieveAndDecrypt()
        file.close()
        print("File saved")
        self.encryptAndSend("File received successfully".encode())

    def interpret(self, msg):
        msgArray = msg.decode().split()
        print("Client request:", msgArray[0], "file:", msgArray[1])
        if(msgArray[0].lower() == "read"):
            self.sendFile(msgArray[1])
        elif(msgArray[0].lower() == "write"):
            self.receiveFile(msgArray[1])
        else:
            self.close("The requested operation is not \"read\" or \"write\"")


    def listen(self):
        while self.alive:
            (connection, address) = self.socket.accept()
            print("Connection accepted from:", address, "at", time.strftime("%c"))
            _thread.start_new_thread(Server.receive, (self, connection))

    def receive(self, connection):
        self.connection = connection
        init = self.connection.recv(1024).decode().split()
        cipher = init[0].strip()
        iv = init[1]
        print("Client desired cipher:", cipher)
        self.aeskey = self.initCrypt(cipher)
        if(self.mode != 0):
            self.cipher = Cipher(algorithms.AES(self.aeskey), modes.CBC(iv), backend=self.backend)
            self.encryptor = self.cipher.encryptor()
            self.decryptor = self.cipher.decryptor()

        #Get the command and file from the client
        self.interpret(self.recieveAndDecrypt())




    #Convert each byte to hex
    def hexdump(self, string):
        bytes = bytearray(string)
        ret = ""
        for i in range(len(bytes)):
            ret = ret + format(bytes[i],  '02x')
            ret = ret + " "
        return ret

    def autoN(self, string):
        bytes = bytearray(string)
        ret = ""
        i = 0
        while i in range(len(bytes)):
            line = ""

            for j in range(min(self.n, (len(bytes)-i))):
                if(32 <= bytes[i+j] <= 127):
                    line = line+(chr(bytes[i+j]))
                elif(bytes[i+j] == self.BACKSLASH or bytes[i+j] == self.TAB or bytes[i+j] == self.NEWLINE or bytes[i+j] == self.CARRIAGE):
                    line = line + repr(chr(bytes[i+j])).strip("\'")
                else:
                    line = line + "\\" + format(bytes[i+j], '02x')
            ret = ret + line + "\n"
            i = i + self.n
        return ret




def main():
    # Call python3 ProxyServer.py [logoptions] source server dest
    if(len(sys.argv) == 3):
        # Default log options
        port = int(sys.argv[1])
        key = sys.argv[2]
        print("Creating transfer server with arguments:")
        print("Port: ", port, "\nKey: ", key)
        server = Server(port, key)
        server.listen()
    else:
        print("Usage: python3 Server.py port key")

main()
