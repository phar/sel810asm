from rs227 import *
import sys
import os

if __name__ == '__main__':
	f = open(sys.argv[1],"rb")
	tape = RS227("%s.227" % ".".join(sys.argv[1].split(".")[:-1]))
	filecontents = f.read(os.path.getsize(sys.argv[1]))
	tape.write_contents(filecontents)


