import socket
import time
from threading import Thread

class Server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    usernames = []
    HOST = 'localhost'
    PORT = 12345

    def __init__(self):
        self.s.bind((self.HOST,self.PORT))
        self.s.listen(3)
        #accept = Thread(target=self.accept_clients) # no args
        #accept.daemon = True
        #accept.start()
        #accept.join()
        #self.s.close()

    def accept_clients(self):
        while True:
            # establish a connection
            clientsocket, address = self.s.accept()

            print(str(address[0]), "on port:", str(address[1]), "connected")
            username = clientsocket.recv(1024).decode('utf8')
            self.usernames.append(username)
            self.connections.append(clientsocket)
            print(username, 'connected')

            # if somone connects then the door opening should play for everyone
            # that is not the person that has just connected
            if len(self.connections) > 1: # then more than one person is connected
                # start a thread to play sound for all the people that are connected
                conThread = Thread(target=self.new_connection, args=[clientsocket, address, username])
                conThread.daemon = True
                conThread.start()


            thread = Thread(target=self.handle_client, args=[clientsocket, address, username])
            thread.daemon = True
            thread.start()

    def handle_client(self, clientsocket, address, username):
        while True:
            data = clientsocket.recv(1024)

            # if the person types out quit
            if data.decode('utf8').lower() == "quit":
                self.connections.remove(clientsocket)
                #print(str(address[0]), "has disconnected")
                print(username, "has disconnected")
                for connection in self.connections:
                    connection.send(bytes("{} has left the chat".format(username), 'utf8'))
                clientsocket.close()

                break
            # then the person signed off probably iwth ctrl-c
            elif not data: # then person has signed off
                self.connections.remove(clientsocket)
                #print(str(address[0]), "has disconnected")
                print(username, "has disconnected")
                for connection in self.connections:
                    connection.send(bytes("{} has left the chat".format(username), 'utf8'))
                clientsocket.close()
                break

            # send data out
            for connection in self.connections:
                connection.send(data)

#============================ if you don't want to send what client just sent
                """
                if connection != clientsocket: # don't want to resend what the client just sent
                    msg = data.decode('utf8')
                    msg = bytes(" [{}] : {}".format(username, msg), 'utf8')
                    connection.send(msg) # don't decode or encode because we'll let client handle that
                """

    # for every new connection notify that the person has joined the chat
    def new_connection(self, clientsocket, address, username):
        for connection in self.connections:
            if connection != clientsocket:
                # send message saying that the person has joined the chat
                connection.send(bytes("{} has joined the chat!".format(username), 'utf8'))



server = Server()
server.accept_clients()
