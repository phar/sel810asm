import struct
import re
import json
import traceback
import sys
from SELOP import *
import array
import time
from rs227 import *


specialaction = ["ORG", "ENDJ", "string", "9 bit add-to", "DAC", "EAC", "turn on chain flag", "turn on load flag", "END"]

def getnmeline(nmemonic="", nmemonicarg=""):
	return "%s\t%s" %(nmemonic,nmemonicarg)

def getline(offset, opcode, nmemonic="", nmemonicarg=""):
	return "%d\t%s\t%08o\t%s" % (l,LOADER_FORMATS[(0xc00000 & v) >> 22][0],opcode,getnmeline(nmemonic,nmemonicarg))



def printline(offset, opcode, nmemonic="", nmemonicarg=""):
	print(getline(offset,opcode,nmemonic,nmemonicarg))



tape = RS227(sys.argv[1])
full_tape = tape.read_contents()

fn = "%s.obj" % ".".join(sys.argv[1].split(".")[:-1])
print("writing output to %s" % fn)
f = open(fn,"wb")
for w in full_tape:
	f.write(struct.pack("3B",(w & 0xff0000) >> 16,(w & 0xff00) >> 8, (w & 0xff)))
f.close()

l = 0
idx = 0
while idx < len(full_tape):
	v = full_tape[idx]
	fmt = (0xc00000 & v) >> 22
	val = v & 0x3fffff
	handled = False
	
	if fmt == 0b00:
		zeros = (val & 0x3f0000) >> 17
		val = v & 0xffff

		if zeros == 0x00:
			buf = "'%06o" % val
			opcode = (val & 0xf000) >> 12
			x = (val & 0x100) >> 8
			i = (val & 0x80) >> 7
			addr = val & 0x1ff
			buf2 = ""
			second_word = False
			
			if opcode == 0: #augmented opcodes
				augmentcode = (val & 0x3f)
				for nme,(x,augcode) in AUGMENTED_OPCODES.items():
					if augmentcode  ==  augcode:
						buf2 = getnmeline(nme,"")
						handled = True
			else:
				for nme,nopcode in MREF_OPCODES.items():
					if opcode  ==  nopcode:
						buf2 = getnmeline(nme,"'%06o" % addr)
						handled = True
						
				opcode = (val & 0xffc0)>>6
				unit = (val & 0x3f)
				for nme,(nopcode,x) in IO_OPCODES.items():
					if opcode  ==  nopcode:
						buf2 = getnmeline(nme,"'%02o" % unit)
						handled = True
		
			printline(l,full_tape[idx],"DATA", "%s\t->\t%s" % (buf,buf2))
			handled = True
		idx += 1

	elif fmt == 0b01:
		r =   (val & 0x200000) >> 21
		x = (val & 0x100) >> 8
		i = (val & 0x80) >> 7
		addr = (val & 0xffff)
		opcode = (val & 0x1e0000) >> 17

		postargs = ""
		indir = ""
		
		if x:
			postargs += ", 1"
		if i:
			indir = "*"

		if opcode == 0: #augmented opcodes
			augmentcode = (val & 0x3f)
			for nme,(x,augcode) in AUGMENTED_OPCODES.items():
				print(augcode,augmentcode)
				if augmentcode  ==  augcode:
					printline(l,full_tape[idx],nme,"")
					handled = True
		else:
			for nme,nopcode in MREF_OPCODES.items():
				if opcode  ==  nopcode:
					printline(l,full_tape[idx],"%s%s" % (nme,indir),"'%06o%s" % (addr,postargs))
					handled = True
		idx += 1

	elif fmt == 0b10:
		idx += 1
		cd = (0xc00000 & full_tape[idx]) >> 22
		if cd == 0x00:
			print("sub def")
		elif cd == 0x01:
			print("sub call")
		elif cd == 0x02:
			print("common def")
		elif cd == 0x03:
			print("common req")
		idx += 3

	elif fmt == 0b11:
		r =   (val & 0x200000) >> 21
		opcode = (val & 0x1e0000) >> 17
		isliteral = val &0x10000


		if(isliteral):
			literal = (val & 0xffff)
			if opcode == 0: #augmented opcodes
				augmentcode = (val & 0x3f)
				for nme,(x,augcode) in AUGMENTED_OPCODES.items():
					print(augcode,augmentcode)
					if augmentcode  ==  augcode:
						printline(l,full_tape[idx],nme,"")
						handled = True
			else:
				for nme,nopcode in MREF_OPCODES.items():
					if opcode  ==  nopcode:
						printline(l,full_tape[idx],"%s" % nme,"='%06o" % literal)
						handled = True

		else:
			address = (val & 0x7fff)
			n = (val & 0x8000) >> 15
			print("****")
			printline(l,full_tape[idx],specialaction[opcode], "'%06x" % address)
			handled = True
		idx += 1
		
	if handled == False:
		printline(l,full_tape[idx] )
	l = l + 1

