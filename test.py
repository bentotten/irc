import copy
# Saves room and client list
initialMsg = ':GUEST! {0.0.0.0, 5000} PRIVMSG #: /JOIN #test\n'    # {IP, port}
msg = "PRIVMSG #cats: Hello World! I'm back!\n"
connection = "<socket.socket fd=5, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 5000), raddr=('127.0.0.1', 41704)>"
client = "('127.0.0.1', 41704)"
message = {'nick': '', 'client': '', 'chan': '', 'cmd': '', 'msg': ''}


class master():
    def __init__(self):
        self.room = {'#': {}}  # Adds first channel 0 as #
        # self.room = {'#': {('127.0.0.1', 41704): 'GUEST'}}  # Adds first channel 0 as #
        self.var = '' # Temp storage

    # Allows client to join or create a new chan
    def eval(self, data, client):
        print('Evaluating data')
        msg = self.parse(data, client)  # Chop raw data up into hashable pieces

        # Add user to new room
        # if msg['cmd'].lower() == 'join'
            # self.join(msg)
        print(f'\nmsg: {msg}')
        print(f'room: {self.room}')

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
            # Finish the string parsing
            string = data.split('PRIVMSG', 1)
            # Parse Channel
            string = string[1].split(':', 1)
            message['chan'] = string[0].lstrip(' ')
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
            message['cmd'] = string[0].lstrip('/')
            message['msg'] = string[1].rstrip('\n')
        else:
            message['msg'] = string[1].rstrip('\n')

        return message

    # Find nick using client
    def find_nick(self, client):
        return self.recursive_find_nick(client, self.room)

    # Find client using nick
    def find_client(self, nick):
        return self.recursive_find_client(nick, self.room)

    def find_chan(self, chan):
        for key in self.room:
            if key is chan:
                print(f'{chan} exists')
                return True
        print(f'{chan} does not exist')
        return False

    def create_chan(self, chan, client):
        # chan_copy = copy.deepcopy(chan)
        self.room[chan] = {}

    # Add client to channel
    def add_client(self, client, chan, nick):
        # If no room, create it
        if not self.find_chan(chan):
            print('Creating new channel')
            self.create_chan(chan, client)

        nick_fetch = self.find_nick(client)
        if nick_fetch is None:
            if nick == '':
                nick = 'Guest'
            self.room[chan][client] = nick
        else:
            self.room[chan][client] = nick_fetch
        print(f'{nick} joined {chan}')


def main():
    channels = master()
    # channels.eval(initialMsg, client)
    channels.eval(msg, client)


if __name__ == '__main__':
    main()
