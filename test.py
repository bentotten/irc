# Saves room and client list
initialMsg = ':NICK! 0 0 0 PRIVMSG #: JOIN\n'
msg = "PRIVMSG #cats: Hello World! I'm back!\n"
connection = "<socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 5000), raddr=('127.0.0.1', 41704)>"
client = "('127.0.0.1', 41704)"
msgFormat = {'nick':'','client':'','key':'','chan':'','cmd':'','msg':''}


class master():
    def __init__(self):
        self.room = {'#': {}}  # Adds first channel 0 as #

    # Allows client to join or create a new chan
    def join(self, data, client):
        print('Join function')
        self.parse(data)
        print(f'room: {self.room}')

    def parse(self, data):
        message = {'nick':'','client':'','key':'','chan':'','cmd':'','msg':''}
        print(message)

        # Pull prefix, if exists
        if data[0] is ':':
            print('I have a prefix!')   # Need to check/add user
            string = data.split('!', 1)
            print(f'Split 1: {string[0]}')
            print(f'Split 2: {string[1]}')
            print(f'Full string: {string}')


def main():
    channels = master()
    print(channels)
    channels.join(initialMsg, client)


if __name__ == '__main__':
    main()
