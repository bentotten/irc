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


def attempt_reconnect(sock):
    i = 0
    connected = False
    while not connected and i < 10:
        try:
            print('Attempting to reconnect...')
            sock.close()    # Close current socket
            sock = connection() # Attempt reconnect
            connected = True
            print('Reconnected to server')

            return True
        except socket.error:
            time.sleep(1)   # Sleep for 1 second if not successful
            i += 1
        finally:
            print('Unable to reconnect')
            return False



# Listens for FIFO and sends messages to server from FIFO
class pipe(threading.Thread):
    # Constructor
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        global stop
        try:
            while stop:
                print("Opening FIFO...")
                with open(clientPath) as fifo:
                    print("FIFO opened")
                    while stop:
                        data = fifo.read()
                        if len(data) == 0:
                            print("Writer closed")
                            break
                        print('Read: "{0}"'.format(data))
                        send(data, self.sock)
        except socket.error as error:
            sys.stderr.write(f'Error: {error}')
            stop = False    # Signal other thread to stop
            self.sock.close()
            #return 1
        finally:
            print(f'Closing Pipe\nStop: {stop}')
            stop = False
            print(f'Stop now: {stop}')
            #return 0


# Listens for messages from the server
class listen(threading.Thread):
    # Constructor
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        global stop
        try:
            while stop:
                data = self.sock.recv(2048)
                print(f'Received "{data}"\n')
                if len(data) == 0:
                    break

        except socket.error as error:
            sys.stderr.write(f'Error: {error}i. Exiting...')
            stop = False
            #return 1

        finally:
            print(f'Closing Listening\nStop: {stop}')
            stop = False
            print(f'Stop now: {stop}')
            n = threading.active_count()
            print(f'Threads: {n}')
            #return 0


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
    # key = read_key()
    # init_msg = f'NICK {nick}\\nUSER 0 0 0 :{nick}\\nJOIN #welcome {key}'
    print(instructions)

    make_io()   # Make client io
    sock = connection()  # Connect to server

    # Start threading
    t1 = pipe(sock)
    t2 = listen(sock)

    # starting thread 1
    x = t1.start()
    # starting thread 2
    t2.start()

    print(f'{x}')

    n = threading.active_count()
    print(f'Threads: {n}')
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
