#!/usr/bin/python -u
# Ben Totten
# CS594 Final Project
# IRC: Client

import sys
import os
from os import path
import socket
import threading
import time
# import re
# import ssl


# Reads in key for server connection
def read_key():
    with open('config.txt', 'r') as file:
        key = file.read()
    return key


# Program initial variables
serverAddress = ('localhost', 5000)
nick = 'Guest'  # User can change this in irc with /nick <NICK>
key = read_key()
client = 'client.io'  # Name of actual FIFO .io
clientPath = './' + client
init_msg = f'NICK {nick}\\nUSER 0 0 0 :{nick}\\nJOIN #welcome {key}'
instructions = 'Welcome to mIRC! To send a message, type "Hello! >> client.io"'

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
        while True:
            print("Opening FIFO...")
            with open(clientPath) as fifo:
                print("FIFO opened")
                while True:
                    data = fifo.read()
                    if len(data) == 0:
                        print("Writer closed")
                        break
                    print('Read: "{0}"'.format(data))
                    send(data, self.sock)


# Listens for messages from the server
class listen(threading.Thread):
    # Constructor
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        # msg = "test test"  # TODO Delete me
        # sock.sendall(msg.encode())
        # send(msg, sock)
        try:
            while True:
                data = self.sock.recv(16)
                print(f'Received "{data}"\n')
                if len(data) == 0:
                    break

        except socket.error as error:
            sys.stderr.write(f'Error: {error}')

        finally:
            print('Closing socket\n')
            self.sock.close()

    # context = ssl.create_default_context()
    # Connect
    # sys.stderr.write(f'Connecting to {serverAddress}')
    # with socket.create_connection(serverAddress) as sock:
        # with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            # print(ssock.version())
            # ssock.send(package.encode())
            # while True:
                # data = ssock.recv(2048)
                # if (len(data) < 1):
                    # break
                # print(data)

    # CLOSE SOCKET CONNECTION
    # ssock.close()


# Send piped inputs to the server
def send(msg, sock):
    try:
        # Send data
        sys.stderr.write(f'Sending "{msg}"\n')
        sock.sendall(msg.encode())
    finally:
        print('Closing socket\n')
        sock.close()


# Main
def main():
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
    t1.join()
    # wait until thread 2 is completely executed
    t2.join()

    # Shutdown connection
    sock.shutdown(socket.SHUT_WR)
    print("Done")


# Launch main
if __name__ == '__main__':
    main()
