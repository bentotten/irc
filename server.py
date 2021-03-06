# Ben Totten
# CS594 Final Project
# IRC: Server

# Issue commands to server by echoing at server.io
# Example: echo "_stop" >> server.io

import os
from os import path
import sys
import socket
import ssl
import re
import threading
import copy
# import subprocess


# path = "./client.io"
# fifo = open(path, "r")
serverAddress = ('localhost', 5000)
server = 'server.io'  # Name of actual FIFO .io
serverPath = './' + server
# Some defaults for testing purposes
initialMsg = ':JACK! {0.0.0.0, 5000} PRIVMSG #cats: /JOIN #test\n'  # {IP,port}
msg = "PRIVMSG #cats: Hello World! I'm back!\n"
qmsg = "PRIVMSG #: /part #cats"
client = "('127.0.0.1', 41704)"
message = {'nick': '', 'client': '', 'chan': '', 'cmd': '', 'msg': ''}


class master():
    def __init__(self):
        self.room = {'#': {}}  # Adds first channel 0 as #
        self.var = ''  # Temp storage

    # Allows client to join or create a new chan
    def eval(self, data, client, sock, connection):
        print('Processing in irc ...')
        msg = self.parse(data, client)  # Chop raw data up into hashable pieces
        print(f'\nMessage received: {msg}')

        # Add user to new room
        if msg['cmd']:
            print(f'Processing Command: {msg["cmd"]}')
            # Join
            if msg['cmd'].lower() == "'/join":
                print('Joining...')
                self.add_client(msg['client'], msg['msg'], msg['nick'])
            # Leave
            elif msg['cmd'].lower() == "'/part'":
                self.rm_client(msg['/client'], msg['chan'], msg['nick'])
            # List Channels
            elif msg['cmd'].lower() == "'/list'" and msg['msg'] == '':
                return self.list(False)
            # List members of a channel
            elif msg['cmd'].lower() == '/list' and msg['msg'] != '':
                return self.list_clients(msg['msg'], False)
        else:
            print('Sending...')
            self.send(msg, connection)

        print(f'Rooms: {self.room}\n')

    def send(self, msg, connection):
        print(f"Sending message to {msg['chan']}")

        # Send message
        for client in self.room[msg['chan']]:
            # Put client back in tuple form
            # result = client.split(',')
            # result[0] = result[0].lstrip(" ('")
            # result[0] = result[0].rstrip("'")
            # result[1] = int(result[1].rstrip(') '))
            # cl = tuple(result)

            connection.sendto(msg['msg'].encode(), client)
            print(f'Message send to {client}')
        return

    # Credit to Tom de Geus on Stackoverflow
    def recursive_find_nick(self, to_match, d):
        for k, v in d.items():
            if isinstance(v, dict):
                self.recursive_find_nick(to_match, v)
            else:
                if to_match is k:
                    print('Client exists {0} : {1}'.format(k, v))
                    self.var = v
                    return v

    # Credit to Tom de Geus on Stackoverflow
    def recursive_find_client(self, to_match, d):
        for k, v in d.items():
            if isinstance(v, dict):
                self.recursive_find_client(to_match, v)
            else:
                if to_match is v:
                    print('Nick exists {0} : {1}'.format(k, v))
                    self.var = k
                    return k

    def parse(self, data, client):
        # Pull prefix, if exists. This will mean prefix should be used to save
        # user data instead of client address; it implies the message was
        # forwarded by another server
        message = {'nick': '', 'client': '', 'chan': '', 'cmd': '', 'msg': ''}

        if data[0] == ':':
            print('\nChecking prefix...')   # Need to check/add user
            # Parse NICK
            string = data.split('!', 1)
            message['nick'] = copy.deepcopy(string[0].lstrip(':'))
            # Parse real Client IP address
            string = string[1].split('PRIVMSG', 1)
            message['client'] = copy.deepcopy(string[0])
            # Parse Channel
            string = string[1].split(':', 1)
            message['chan'] = copy.deepcopy(string[0].lstrip(' '))
            # Add client to initial channel
            self.add_client(client, message['chan'], message['nick'])

        # Else strip PRIVMSG off of front. Needs double for chan to get in []
        else:
            print('Parsing message...')
            # Finish the string parsing
            string = data.split('PRIVMSG', 1)
            # Parse Channel
            string = string[1].split(':', 1)
            message['chan'] = copy.deepcopy(string[0].lstrip(' '))
            self.add_client(client, message['chan'], message['nick'])
            # Fill out client and nick
            self.var = None
            self.find_nick(client)
            if self.var is None:
                self.add_client(client, message['chan'], message['nick'])
                self.var = None
                self.find_nick(client)
            message['client'] = copy.deepcopy(client)
            message['nick'] = copy.deepcopy(self.var)

        # Everyone gets cmd parsed, if it exists
        if string[1].find('/', 1, 2) == 1:
            temp = string[1].lstrip(' /')
            string = temp.split(' ')
            message['cmd'] = copy.deepcopy(string[0].lstrip('/'))
            if len(string) == 2:
                message['msg'] = copy.deepcopy(string[1].rstrip('\n'))
        else:
            message['msg'] = copy.deepcopy(string[1].rstrip('\n'))
        return message

    # Find nick using client
    def find_nick(self, client):
        return self.recursive_find_nick(client, self.room)

    # Find client using nick
    def find_client(self, nick):
        return self.recursive_find_client(nick, self.room)

    def find_chan(self, chan):
        print(f'Checking {chan}')
        for key in self.room.keys():
            if chan == key:
                print(f'{chan} exists')
                return True
        print(f'{chan} does not exist')
        return False

    def create_chan(self, chan, client):
        self.room[chan] = {}
        return

    # Add client to channel
    def add_client(self, client, chan, nick):
        # If no room, create it
        if not self.find_chan(chan):
            print('Creating new channel')
            self.create_chan(chan, client)

        # Check if already in room
        array = self.list_client(chan, False)
        if client in array:
            print('Client already in channel')
        else:
            print(f'Adding ${client} to ${chan}')
            nick_fetch = self.find_nick(client)
            nick_fetch = copy.deepcopy(self.var)
            if nick_fetch == '':
                print('Nick not found.')
                if nick == '':
                    nick = 'Guest'
                else:
                    self.room[chan][client] = copy.deepcopy(nick)
                    print(f'{nick} joined {chan}')
            else:
                self.room[chan][client] = copy.deepcopy(nick_fetch)
                print(f'{nick_fetch} joined {chan}')
        return

    def rm_client(self, client, chan, nick):
        print(f'{client} [{nick}] parting from {chan}')
        if self.find_chan(chan):
            del self.room[chan][client]
            if self.room[chan] == {}:
                print(f'{chan} is an empty room. Deleting...')
                del self.room[chan]
        else:
            print(f'Unable to find {chan}')

    # Returns all channels
    def list(self, silent):
        rlist = []
        for key in self.room.keys():
            rlist.append(key)
        if silent is False:
            print(f'\nLIST: All channels: {rlist}')
        return rlist

    # Returns a channels members
    def list_client(self, chan, silent):
        if self.find_chan(chan):
            rlist = []
            for key in self.room[chan]:
                rlist.append(self.room[chan][key])
            if silent is False:
                print(f'\nLIST: All clients in {chan}: {rlist}')
            return rlist
        else:
            print('Error: Invalid channel')
            return None


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# Removes old pipe
def rm_old():
    print(f'Searching for {server}')
    status = path.exists(server)    # Check existance of io
    if status is False:             # If doesnt exist, return
        print(f'{server} cleared')
        return 0
    else:                           # If file exists, delete it
        print(f'Attempting to remove {server}')
        os.remove(server)
        if path.exists(server) is True:
            print(f'Error: Unable to delete {server}')
            return 1
        else:
            return 0


# Makes new pipe
def make_io():
    if rm_old() == 0:   # Remove old client.io
        if os.name == 'posix':   # If running on a linux system
            print('Creating IO')
            os.mkfifo(serverPath)
            print('IO success')
        elif os.name == 'nt':  # If running on a windows system
            print('Windows Operating system not supported')

        else:
            print('Unsupported Operating System. Please run on Linux')
            return 1
    else:
        return 1


def disconnect(client, connection):
    print(f'{client} disconnecting')
    connection.close()


def check(raw, client, connection):
    data = raw.decode()
    print(f'Checking data: {data}')
    if data == '':
        return None
    elif 'ip_, port_' in data:
        print('Initial connection message')
        data = data.replace('ip_, port_', str(client), 1)
        return data
    elif data[0] == '_':
        data = data.strip().lower()
        data = re.sub(r'\W+', '', data)
        print(f'Data: {data}')
        if data == "_disconnect":   # To disconnect client
            disconnect(client, connection)
            return data
    else:
        return data


class pipe(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = True

    def run(self):
        try:
            while self.stop:
                print("Opening FIFO...")
                with open(serverPath) as fifo:
                    print("FIFO opened")
                    while True:
                        data = fifo.read()
                        check = re.sub(r'\W+', '', data)
                        if '_stop' == check:    # If user is closing client
                            print('Stopping Server')
                            self.stop = False
                            return
                        elif len(data) == 0:
                            print("Writer closed")
                            break
                        else:
                            print('Server Command not found: "{0}"'.format(data))
        except socket.error as error:
            sys.stderr.write(f'Server Pipe Error: {error}')
        finally:
            print('Closing Server Pipe')


class connect(threading.Thread):
    # Constructor
    def __init__(self, connection, clientAddress, irc, sock):
        threading.Thread.__init__(self)
        self.connection = connection
        self.clientAddress = clientAddress
        self.irc = irc
        self.sock = sock
        self.stop = True

    def run(self):
        connection = self.connection
        clientAddress = self.clientAddress
        irc = self.irc
        sock = self.sock
        # try:
        if 1 == 1:
            print(f'Connection from {clientAddress}')
            # Get data in chunks
            while True:
                data = connection.recv(512)  # Message size limit: 512b
                print('received "%s"' % data)
                # Check for commands from client
                data = check(data, clientAddress, connection)
                # Send data to connected clients
                if data:
                    print('Evaluating data')
                    irc.eval(data, clientAddress, sock, connection)
                    # connection.sendall(data)
                else:
                    print(f'No more data from {clientAddress}')
                    break
        # except socket.error as error:
            # sys.stderr.write(f'Error: {error}')
            # sys.stderr.write('Client abruptly disconnected')
            # self.stop = False
        # finally:
            # Close connection
            # print('Closing connection')
            # connection.close()


def main():
    # Make data structure to hold all clients and rooms
    clients = []
    threadcount = 0
    irc = master()
    make_io()   # Setups up pipe
    # Spin up FIFO listener
    t1 = pipe()
    t1.setDaemon(True)  # Set to non-blocking thread
    t1.start()

    # Load SSL cert
    try:
        print('Loading SSL certificate')
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="certificate.crt", keyfile="certificate.key")
    except OSError:
        sys.stderr.write('If no cert found, run: ./make_cert.sh")')

    # Create TCP/IP scoket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            # Bind to port
            print('starting up on %s port %s' % serverAddress)
            sock.bind(serverAddress)
            # Listen for incomming connections
            sock.listen(5)

            # Format new incoming client connections as new threads
            while t1.is_alive():
                # Handle new connection
                print('waiting for a connection')
                connection, clientAddress = sock.accept()

                # Start new thread for new connections
                clients.append(connect(connection, clientAddress, irc, sock))
                threadcount += 1
                clients[-1].setDaemon(True)
                clients[-1].start()

    except socket.error as error:
        sys.stderr.write(f'ERROR: {error}\n')
        sock.close()


if __name__ == '__main__':
    main()
