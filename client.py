#!/usr/bin/python -u
# Ben Totten
# CS594 Final Project
# IRC: Client

import sys
import re

nick = 'Guest'  # User can change this in irc with /nick <NICK>
key = ''


# Reads in key for server connection
def read_key():
    with open('config.txt', 'r') as file:
        key = file.read()
    print(key)


def main():
    read_key():


# Launch main
if __name__ == "__main__":
    main()
