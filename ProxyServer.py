import socket
import sys
import time
import _thread
import re
class Server:
    MAX_CLIENTS = 5
    AUTH_MSG = 0
    PASS = "pass"

    # Character constants
    BACKSLASH = ord('\\')
    TAB = ord('\t')
    NEWLINE = ord('\n')
    CARRIAGE = ord('\r')


    def __init__(self, inPort, outPort, address, outputMode, n):
        self.inPort = inPort
        self.outPort = outPort
        self.address = socket.gethostbyname(address)
        self.outputMode = outputMode
        self.n = n

    def printInput(self, data):
        if self.outputMode == 1:
            print("<-- " + data.decode())
        elif self.outputMode == 2:
            print("<-- " + re.sub(r'[^\x00-\x7F]+',' ', data.decode()))
        elif self.outputMode == 3:
            print("<-- " + self.hexdump(data))
        elif self.outputMode == 4:
            print("<-- " + self.autoN(data))


    def printOutput(self, data):
        if self.outputMode == 1:
            print("--> " + data.decode())
        elif self.outputMode == 2:
            print("--> " + re.sub(r'[^\x00-\x7F]+',' ', data.decode()))
        elif self.outputMode == 3:
            print("--> " + self.hexdump(data))
        elif self.outputMode == 4:
            print("--> " + self.autoN(data))



    def listen(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.bind(('', self.inPort))
        clientSocket.listen(Server.MAX_CLIENTS)
        print("Waiting for connection on port" , self.inPort)
        while True:
            (connection, address) = clientSocket.accept()
            print("Connection accepted from:", address, "at", time.strftime("%c"))
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.connect((self.address, self.outPort))
            self.alive = True
            tgt = Server
            _thread.start_new_thread(Server.clientToServer, (self, connection, serverSocket))
            _thread.start_new_thread(Server.serverToClient, (self, connection, serverSocket))

    def clientToServer(self, client, server):
        while self.alive:
            toSend = client.recv(1024);
            if(toSend.decode() is ""):
                break
            self.printOutput(toSend)
            server.send(toSend)


    def serverToClient(self, client, server):
        # Open outbound connection
        while self.alive:
            toSend = server.recv(1024)
            if (toSend.decode() is ""):
                break
            self.printInput(toSend)
            client.send(toSend)

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
    if(len(sys.argv) == 5):
        # Parse for log options
        source = int(sys.argv[2])
        server = sys.argv[3]
        dest = int(sys.argv[4])
        n = 0 # for autoN initialization
        if(sys.argv[1] == "-raw"):
            # All data = ascii
            log = 1
        elif(sys.argv[1] == "-strip"):
            # Only printable characters printed
            log = 2
        elif(sys.argv[1] == "-hex"):
            # All data in hexdump -C form
            log = 3
        elif("-auto" in sys.argv[1]):
            # Data divided into N byte chunks, displayed separate
            n = int(re.search(r'\d+', sys.argv[1]).group())
            log = 4
        print("Creating proxy server with arguments:")
        print("Source: ", source, "\nDestination: ", dest, "\nServer: ", server, "\nLog mode: ", log)
        server = Server(source, dest, server, log, n)
        server.listen()

    elif(len(sys.argv) == 4):
        # Default log options
        source = int(sys.argv[1])
        server = sys.argv[2]
        dest = int(sys.argv[3])
        log = 0
        print("Creating proxy server with arguments:")
        print("Source: ",source , "\nDestination: ", dest , "\nServer: ", server, "\nLog mode: " , log)
        server = Server(source, dest, server, log, 0)
        server.listen()
    else:
        print("Usage: python3 ProxyServer.py [logoptions] sourcePort server destPort")

main()
print("end")






