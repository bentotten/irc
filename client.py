#!/usr/bin/python -u
# Ben Totten
# CS594 Final Project
# IRC: Client

import sys
import re
import os
from os import path
import subprocess


nick = 'Guest'  # User can change this in irc with /nick <NICK>
key = ''
client = 'client.io'  # Name of actual FIFO .io


# Reads in key for server connection
def read_key():
    with open('config.txt', 'r') as file:
        key = file.read()
    print(key)


def rm_old():
    print(f'Searching for {client}')
    status = path.exists(client)    # Check existance of io
    if status == False:             # If doesnt exist, return
        print(f'{client} cleared')
        return
    else:                           # If file exists, delete it
        print(f'Attempting {bashCommand}')
        os.remove(client)
        if path.exists(client) is True:
            print(f'Error: Unable to delete {client}')
        return

def main():
    read_key()  # Read key for server
    rm_old()    # Remove old client.io
    


# Launch main
if __name__ == '__main__':
    main()
