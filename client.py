#!/usr/bin/python -u
# Ben Totten
# CS594 Final Project
# IRC: Client

# Use provided code to send messages by typing './m <MESSAGE>'
# Commands:
# _stop        : Client disconnects from server and exits
# _disconnect  : Client signals server to disconnect client

import sys
import os
from os import path
import socket
import threading
import time
import re
# import ssl


# Program initial variables
serverAddress = ('Localhost', 5000)
nick = 'BEN'  # User can change this in irc with /nick <NICK>
client = 'client.io'  # Name of actual FIFO .io
clientPath = './' + client
instructions = 'Welcome to b-IRC! To send a message, type "./m Hello!"'
msg = {'nick': '', 'client': '', 'chan': '', 'cmd': '', 'msg': ''}


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


# Create a TCP/IP socket and send registration message
# Registration message example
# :JACK! {<IP>, <PORT>} PRIVMSG #: /JOIN #test\n'  # {IP,port}
def connection():
    sock = socket.create_connection(serverAddress)
    # Port and IP will be filled in on the server side
    text = ':' + nick + '! {ip_, port_} PRIVMSG #: /JOIN #\n'
    print(text)
    sock.sendall(text.encode())
    return sock

def attempt_reconnect(sock):
    print('Attemping reconnect:')
    sock.close()
    for i in range(5):
        try:
            sock = connection()
            print('Reconnected to server!')
            return sock
        except socket.error:
            print('.')
            time.sleep(3)
    print('Unable to reconnect to server.')


# Listens for FIFO and sends messages to server from FIFO
class pipe(threading.Thread):
    # Constructor
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.stop = True

    def run(self):
        try:
            while self.stop:
                print("Opening FIFO...")
                with open(clientPath) as fifo:
                    print("FIFO opened")
                    while True:
                        data = fifo.read()
                        check = re.sub(r'\W+', '', data)
                        if '_stop' == check:    # If user is closing client
                            print('Stop command. Stopping client')
                            self.stop = False
                            break
                        elif len(data) == 0:
                            print("Writer closed")
                            break
                        else:
                            print('Read: "{0}"'.format(data))
                            send(data, self.sock)
        except socket.error as error:
            sys.stderr.write(f'Error: {error}')
        finally:
            print('Closing Pipe')


# Listens for messages from the server
class listen(threading.Thread):
    # Constructor
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.stop = True

    def run(self):
        try:
            while self.stop:
                data = self.sock.recv(2048)
                print(f'Received "{data}"\n')
                if len(data) == 0:      # If server disconnect
                    print('Server abrupt disconnect.')
                    return 1

        except socket.error as error:
            sys.stderr.write(f'Error: {error}')

        finally:
            print('Closing Listening')
            return


# Send piped inputs to the server
# Formats
# "PRIVMSG #cats: Hello World! I'm back!\n"
def send(text, sock):
    try:
        # Add needed header
        msg['nick'] = nick
        # Send data
        print(f'Sending "{msg}"\n')
        sock.sendall(text.encode())
    finally:
        print(f'{msg} sent\n')


# Main
def main():
    # key = read_key()
    # init_msg = f'NICK {nick}\\nUSER 0 0 0 :{nick}\\nJOIN #welcome {key}'
    print(instructions)

    make_io()   # Make client io
    sock = connection()  # Connect to server

    # Start threading and set as Daemons
    t1 = pipe(sock)
    t2 = listen(sock)
    t1.setDaemon(True)  # Set to non-blocking thread
    t2.setDaemon(True)  # Set to non-blocking thread

    # starting thread 1
    t1.start()
    # starting thread 2
    t2.start()

    t1.join(3)
    print('Joined thread 1')
    t2.join(3)
    print('Joined thread 2')

    print('Is t1 alive?')
    print(t1.is_alive())    # Check if T1 timed out
    print('Is t2 alive?')
    print(t2.is_alive())    # Check if T2 timed out

    while t1.is_alive() and t2.is_alive():
        t1.join(3)
        t2.join(3)
    # If server disconnect, t2 will be dead
    if not t2.is_alive():
        sock = attempt_reconnect(sock)

    # Shutdown connection
    # sock.shutdown(socket.SHUT_WR)
    print('Closing socket connection')
    sock.close()
    print("Thank you for using b-IRC!\nExiting")


# Launch main
if __name__ == '__main__':
    main()
