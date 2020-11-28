import os
import sys

path = "./client.io"
fifo = open(path, "r")
for line in fifo:
    print("Received: " + line,)
fifo.close()
