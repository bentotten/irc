# TODO:
# - Make new client connections run on their own thread, to be killed on their
# own thread

# import os
import sys
import socket
import ssl
import re
# import subprocess


# path = "./client.io"
# fifo = open(path, "r")
serverAddress = ('localhost', 5000)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def check(data, client, connection):
    data = str(data.decode().strip().lower())
    re.sub(r'[^a-zA-Z0-9]', '', data)
    print(f'Data: {data}')
    if data == "'disconnect'":
        print(f'{client} disconnecting')
        connection.close()
        print(f'{client} has disconnected')


def main():
    # for line in fifo:
    #   print("Received: " + line,)
    # fifo.close()

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
        while True:
            print('waiting for a connection')
            connection, clientAddress = sock.accept()

            # On connection
            try:
                print(f'Connection from {clientAddress}')

                # Get data in chunks and retransmit it
                while True:
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
                connection.close()


if __name__ == '__main__':
    main()
