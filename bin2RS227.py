from rs227 import *
import sys
import os

if __name__ == '__main__':
	baseaddress = 0x0000
	
	f = open(sys.argv[1],"rb")
	tape = RS227("%s.227" % ".".join(sys.argv[1].split(".")[:-1]))
	
	filecontents += LOADER_FORMATS[LITERAL_LOAD][1] | baseaddress
	filecontents += f.read(os.path.getsize(sys.argv[1])) #fixmme encode in 24 bit
	
	tape.write_contents(filecontents)


0000 1011 0000 1010 0000

0000 0000 0010 1100 0000
