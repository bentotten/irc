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
# import subprocess


# path = "./client.io"
# fifo = open(path, "r")
serverAddress = ('localhost', 5000)
server = 'server.io'  # Name of actual FIFO .io
serverPath = './' + server


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


def check(data, client, connection):
    data = str(data.decode().strip().lower())
    data = re.sub(r'\W+', '', data)
    print(f'Data: {data}')
    if data == "_disconnect":   # To disconnect client
        print(f'{client} disconnecting')
        connection.sendall(data.encode())
        connection.close()
        print(f'{client} has disconnected')


# Listens for FIFO and sends messages to server from FIFO
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
                            break
                        elif len(data) == 0:
                            print("Writer closed")
                            break
                        else:
                            print('Server Command not found: "{0}"'.format(data))
        except socket.error as error:
            sys.stderr.write(f'Server Pipe Error: {error}')
        finally:
            print('Closing Server Pipe')


# Saves room and client list
class master():
    def __init__(self):
        self.room = [{}]


def main():
    make_io()   # Setups up pipe
    t1 = pipe()
    t1.setDaemon(True)  # Set to non-blocking thread
    t1.start()

    print('If no cert found, run: ./make_cert.sh")')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="certificate.crt", keyfile="certificate.key")

    # Create TCP/IP scoket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        # Bind to port
        print('starting up on %s port %s' % serverAddress)
        sock.bind(serverAddress)

        # Listen for incomming connections
        sock.listen(1)
        # with context.wrap_socket(sock, server_side=True) as ssock:
        #    # print('waiting for a connection')
        #    # connection, clientAddress = ssock.accept()
        while t1.is_alive():
            print('waiting for a connection')
            connection, clientAddress = sock.accept()
            print('BEN')
            print(connection)
            print(clientAddress)

            # On connection
            try:
                print(f'Connection from {clientAddress}')

                # Get data in chunks and retransmit it
                while t1.is_alive():
                    data = connection.recv(2048)
                    print('received "%s"' % data)
                    # Check for commands
                    check(data, clientAddress, connection)
                    # Send data to connected clients
                    if data:
                        print('sending data back to the client')
                        connection.sendall(data)
                    else:
                        print(f'No more data from {clientAddress}')
                        break
            except socket.error as error:
                sys.stderr.write(f'Error: {error}')
                sys.stderr.write('Client abruptly disconnected')
            finally:
                # Close connection
                print('Closing connection')
                connection.close()


if __name__ == '__main__':
    main()
