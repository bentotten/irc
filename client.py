#!/usr/bin/python -u
# Ben Totten
# CS594 Final Project
# IRC: Client

import sys
import os
from os import path
import socket
import threading
# import re
# import ssl




# Program initial variables
serverAddress = ('Localhost', 5000)
nick = 'Guest'  # User can change this in irc with /nick <NICK>
client = 'client.io'  # Name of actual FIFO .io
clientPath = './' + client
instructions = 'Welcome to b-IRC! To send a message, type "./m Hello!"'
stop = True


# Reads in key for server connection
def read_key():
    with open('config.txt', 'r') as file:
        key = file.read()
    return key


# Removes old pipe
def rm_old():
    print(f'Searching for {client}')
    status = path.exists(client)    # Check existance of io
    if status is False:             # If doesnt exist, return
        print(f'{client} cleared')
        return 0
    else:                           # If file exists, delete it
        print(f'Attempting to remove {client}')
        os.remove(client)
        if path.exists(client) is True:
            print(f'Error: Unable to delete {client}')
            return 1
        else:
            return 0


# Makes new pipe
def make_io():
    if rm_old() == 0:   # Remove old client.io
        if os.name == 'posix':   # If running on a linux system
            print('Creating IO')
            os.mkfifo(clientPath)
            print('IO success')
        elif os.name == 'nt':  # If running on a windows system
            print('Windows Operating system not supported')

        else:
            print('Unsupported Operating System. Please run on Linux')
            return 1


# Create a TCP/IP socket
def connection():
    return socket.create_connection(serverAddress)


# Listens for FIFO and sends messages to server from FIFO
class pipe(threading.Thread):
    # Constructor
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        global stop
        while stop:
            print("Opening FIFO...")
            try:
                with open(clientPath) as fifo:
                    print("FIFO opened")
                    while True:
                        data = fifo.read()
                        if len(data) == 0:
                            print("Writer closed")
                            break
                        print('Read: "{0}"'.format(data))
                        send(data, self.sock)
            except socket.error as error:
                sys.stderr.write(f'Error: {error}i. Exiting...')
                stop = False
                self.sock.close()
                return
            finally:
                print('Closing')
                stop = False
                return


# Listens for messages from the server
class listen(threading.Thread):
    # Constructor
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        global stop
        try:
            while True:
                data = self.sock.recv(2048)
                print(f'Received "{data}"\n')
                if len(data) == 0:
                    break

        except socket.error as error:
            sys.stderr.write(f'Error: {error}i. Exiting...')
            stop = False
            return

        finally:
            print('Closing Listening\n')
            stop = False
            return


# Send piped inputs to the server
def send(msg, sock):
    try:
        # Send data
        print(f'Sending "{msg}"\n')
        sock.sendall(msg.encode())
    finally:
        print(f'{msg} sent\n')


# Main
def main():
    key = read_key()
    init_msg = f'NICK {nick}\\nUSER 0 0 0 :{nick}\\nJOIN #welcome {key}'
    print(instructions)

    make_io()   # Make client io
    sock = connection() # Connect to server

    # Start threading
    t1 = pipe(sock)
    t2 = listen(sock)

    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()

    # wait until thread 1 is completely executed
    print('Joining thread 1')
    t1.join()
    # wait until thread 2 is completely executed
    print('Joining thread 2')
    t2.join()

    # Shutdown connection
    sock.shutdown(socket.SHUT_WR)
    sock.close()
    print("Thank you for using b-IRC!\nExiting")


# Launch main
if __name__ == '__main__':
    main()
