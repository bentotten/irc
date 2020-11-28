#!/usr/bin/python -u
# Ben Totten
# CS594 Final Project
# IRC: Client

import sys
# import re
import os
from os import path
import socket
# import ssl
serverAddress = ('localhost', 5000)

nick = 'Guest'  # User can change this in irc with /nick <NICK>
key = ''
client = 'client.io'  # Name of actual FIFO .io
clientPath = './' + client


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
            os.mkfifo(clientPath)
        elif os.name == 'nt':  # If running on a windows system
            print('Windows Operating system not supported')

        else:
            print('Unsupported Operating System. Please run on Linux')
            return 1


# Connects to server with correct naming
def connect(key):
    msg = f'NICK {nick}\\nUSER 0 0 0 :{nick}\\nJOIN #welcome {key}'
    print('Writing to pipe')
    fifo = open(clientPath, "w")
    fifo.write(msg)
    fifo.close()
    print('success')


def foo():
    # package = "SOCKET WORKING"
    # hostname = serverAddress[0]
    # port = serverAddress[1]

    # Create a TCP/IP socket
    sock = socket.create_connection(serverAddress)

    try:
        # Send data
        message = 'This is the message.  It will be repeated.'
        sys.stderr.write(f'Sending "{message}"\n')
        sock.sendall(message.encode())

        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            sys.stderr.write(f'Received "{data}"\n')

    finally:
        sys.stderr.write('Closing socket\n')
        sock.close()

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


# Main
def main():
    # key = read_key()  # Read key for server
    make_io()   # Make client io
    # connect(key)
    foo()


# Launch main
if __name__ == '__main__':
    main()
