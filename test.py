# Saves room and client list
initialMsg = ':GUEST! {0.0.0.0, 5000} PRIVMSG #: /JOIN #test\n'    # {IP, port}
msg = "PRIVMSG #cats: Hello World! I'm back!\n"
connection = "<socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 5000), raddr=('127.0.0.1', 41704)>"
client = "('127.0.0.1', 41704)"
message = {'nick': '', 'client': '', 'chan': '', 'cmd': '', 'msg': ''}


class master():
    def __init__(self):
        self.room = {'#': {}}  # Adds first channel 0 as #

    # Allows client to join or create a new chan
    def eval(self, data, client):
        print('Join function')
        msg = self.parse(data, client)  # Chop raw data up into hashable pieces

        # Add user to new room
        # if msg['cmd'].lower() == 'join'
            # self.join(msg)
        print(f'msg: {msg}')
        print(f'room: {self.room}')

    def parse(self, data, client):
        # Pull prefix, if exists. This will mean prefix should be used to save
        # user data instead of client address; it implies the message was
        # forwarded by another server
        message = {'nick': '', 'client': '', 'chan': '', 'cmd': '', 'msg': ''}

        if data[0] == ':':
            print('\nChecking prefix...')   # Need to check/add user
            # Parse NICK
            string = data.split('!', 1)
            message['nick'] = string[0].lstrip(':')
            # Parse real Client IP address
            string = string[1].split('PRIVMSG', 1)
            message['client'] = string[0]
            # Parse Channel
            string = string[1].split(':', 1)
            message['chan'] = string[0].lstrip(' ')

        # Else strip PRIVMSG off of front. Needs double for chan to get in []
        else:
            print('Parsing message...')
            # Fill out client and nick

            # Finish the string parsing
            string = data.split('PRIVMSG',1)
            # Parse Channel
            string = string[1].split(':', 1)
            message['chan'] = string[0].lstrip(' ')

        # Everyone gets cmd parsed, if it exists
        if string[1].find('/', 1, 2) == 1:
            temp = string[1].lstrip(' /')
            string = temp.split(' ')
            message['cmd'] = string[0].lstrip('/')
            message['msg'] = string[1].rstrip('\n')
        else:
            message['msg'] = string[1].rstrip('\n')

        return message


        # TODO CHECK TABLE FOR CLIENT IP ADDRESS AND ADD NICK TO MSG


def main():
    channels = master()
    print(channels)
    channels.eval(initialMsg, client)
    channels.eval(msg, client)


if __name__ == '__main__':
    main()
