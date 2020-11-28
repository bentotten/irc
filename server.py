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
#    for line in fifo:
#        print("Received: " + line,)
#    fifo.close()

    sys.stderr.write('If no cert found, run:  context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="cert.pem")

    # Create TCP/IP scoket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        # Bind to port
        sys.stderr.write('starting up on %s port %s' % serverAddress)
        sock.bind(serverAddress)

        # Listen for incomming connections
        sock.listen(5)
        with context.wrap_socket(sock, server_side=True) as ssock:
            sys.stderr.write('waiting for a connection')
            connection, clientAddress = ssock.accept()


if __name__ == '__main__':
    main()
