import struct
from SELOP import *
import os
import sys

def SELDISASM(opcode):
	op = (opcode & 0xf000) >> 12
	nmemonic = ""
	args = ""
	second_word = False
	indir = ""
	
	if op == 0x00: #augmented opcodes
		augmentcode = (opcode & 0x3f)
		shifts      = (opcode & 0x3c0) >> 6
		for nme,(x,augcode) in AUGMENTED_OPCODES.items():
			if augmentcode  ==  augcode:
				nmemonic = nme
				if shifts > 0:
					args = "%d" % shifts
	else:
	
		for nme,nopcode in MREF_OPCODES.items():
			if op  ==  nopcode:
				index    =  (opcode & 0x800) >> 11
				indirect =  (opcode & 0x400) >> 10
				map_bit  =  (opcode & 0x200) >> 9
				addr     = opcode & 0x1ff
				nmemonic = nme
				
				args = "'%06o" % addr
				if index:
					args = args + ", 1"
					
				if indirect:
					indir = "*"
				break

		op = (opcode & 0xff80) >> 12
		for nme,(nopcode,aug) in IO_OPCODES.items():
			augment    = (opcode & 0x180) >> 6
			if (op == nopcode) & (aug ==augment):
				merge_bit  =  (opcode & 0x800) >> 11
				indirect   =  (opcode & 0x400) >> 10
				map_bit    =  (opcode & 0x200) >> 9
				wait_bit   =  (opcode & 0x40) >> 6
				unit       = (opcode & 0x3f)
				
				args = args + "%d" % unit
				if wait_bit:
					args = args + ", W"
				if merge_bit:
					args = args + ", R"
				if indirect:
					indir = "*"

				if nme in["CEU","TEU"]:
					second_word = True #fixme CEU/TEU
				nmemonic = nme
				break

		op = opcode
		for nme,(nopcode,x) in INT_OPCODES.items():
			if op  ==  nopcode:
				augment = opcode & 0x3f
				nmemonic = nme
				break
				
	if nmemonic=="":
		nmemonic = "DATA"
		args = "'%06o" % opcode
				
	return (opcode, nmemonic, indir,  args,second_word)

			
if __name__ == '__main__':
	file= sys.argv[1]
	size = os.path.getsize(file)

	f = open(file,"rb")
	b = f.read(size)

	binfile = struct.unpack(">%dH" % (size/2), b)

	second_word = False
	i = 0
	for val in  binfile:
		val2 = SELDISASM(val)
		if second_word == False:
			second_word = val2[-1]
			print("%06o\t\t%s%s\t%s" % val2[:-1])
		else:
			print("%06o\t\tDATA\t'%06o" % (val2[0],val))
			second_word = False

		i+=1
