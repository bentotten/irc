# import os
import sys
import socket
import ssl
# import subprocess

# path = "./client.io"
# fifo = open(path, "r")
serverAddress = ('localhost', 5000)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    # for line in fifo:
        # print("Received: " + line,)
    # fifo.close()

    sys.stderr.write('If no cert found, run:  context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")

    # Create TCP/IP scoket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        # Bind to port
        sys.stderr.write('starting up on %s port %s' % serverAddress)
        sock.bind(serverAddress)

        # Listen for incomming connections
        sock.listen(1)
        # with context.wrap_socket(sock, server_side=True) as ssock:
            # sys.stderr.write('waiting for a connection')
            # connection, clientAddress = ssock.accept()
        while True:
            sys.stderr.write('waiting for a connection')
            connection, clientAddress = sock.accept()

            # On connection
            try:
                sys.stderr.write(f'Connection from {clientAddress}')

                # Get data in chunks and retransmit it
                while True:
                    data = connection.recv(16)
                    sys.stderr.write('received "%s"' % data)
                    # Send data to connected clients
                    if data:
                        sys.stderr.write('sending data back to the client')
                        connection.sendall(data)
                    else:
                        sys.stderr.write(f'No more data from {clientAddress}')
                        break
            finally:
                # Close connection
                connection.close()


if __name__ == '__main__':
    main()
