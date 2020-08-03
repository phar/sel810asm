import struct
from SELOP import *
import os
import sys

def ceu_breakdown(hint, word):
	outstring = []
	for n,v in CEU_SECOND_WORDS[hint[0]].items(): #fixme hint[0] is just assumed but i need to work the list to figure out the right one
		if n == 'wordmask':
			if (word & v[0]) != v[0]:
				raise ValueError #still temporary
		else:
			if (v[0] & word) >> v[1]:
				outstring.append(n)

	return ",".join(outstring)
	
	
def teu_breakdown(hint, word):
	outstring = []
	for n,v in TEU_SECOND_WORDS[hint[0]].items():#fixme hint[0] is just assumed but i need to work the list to figure out the right one
		if n == 'wordmask':
			if (word & v[0]) != v[0]:
				raise ValueError #still temporary
		else:
			if (v[0] & word) >> v[1]:
				outstring.append(n)

	return ",".join(outstring)
	
	
def SELDISASM(opcode):
	op = (opcode & 0xf000) >> 12
	nmemonic = ""
	args = ""
	second_word = False
	indir = ""
	second_word_hint = None
	comment = None
	
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
				
				args = "'%o" % addr
				if index:
					args = args + ", 1"
					
				if indirect:
					indir = "*"
				break

		op = (opcode & 0xff80) >> 12
		for nme,(nopcode,aug) in IO_OPCODES.items():
			augment    = (opcode & 0x180) >> 7
			if (op == nopcode) & (aug ==augment):
				nmemonic = nme
				merge_bit  =  (opcode & 0x800) >> 11
				indirect   =  (opcode & 0x400) >> 10
				map_bit    =  (opcode & 0x200) >> 9
				wait_bit   =  (opcode & 0x40) >> 6
				unit       = (opcode & 0x3f)
				
				args = args + "'%02o" % unit
				if wait_bit:
					args = args + ", W"
				if merge_bit:
					args = args + ", R"
				if indirect:
					indir = "*"
										

				if nme in SECOND_WORD_OPS:
					second_word = True #fixme CEU/TEU
					if nme == "CEU":
						for a,(n,ch,th) in CEU_TEU_UNITS.items():
							if unit == a:
								second_word_hint = (ceu_breakdown,ch)
								
					elif nme == "TEU":
						for a,(n,ch,th) in CEU_TEU_UNITS.items():
							if unit == a:
								second_word_hint = (teu_breakdown,hh)
					

				if unit not in CEU_TEU_UNITS:
					comment = "unknown unit"
				else:
					if comment != None:
						comment += ", "
					elif comment == None:
						comment = ""
#					print(unit)
					comment +=  "%s unit"  % CEU_TEU_UNITS[unit][0]
				break

		op = opcode
		for nme,(nopcode,x) in INT_OPCODES.items():
			if op  ==  nopcode:
				augment = opcode & 0x3f
				nmemonic = nme
				break
				
	if nmemonic=="":
		nmemonic = "DATA"
		args = "'%o" % opcode
				
	return (opcode, nmemonic, indir,  args,comment, second_word, second_word_hint)

			
if __name__ == '__main__':
	file= sys.argv[1]
	size = os.path.getsize(file)

	f = open(file,"rb")
	b = f.read(size)

	binfile = struct.unpack(">%dH" % (size/2), b)

	second_word = False
	i = 0
	for val in  binfile:
		if second_word == False:
			(opcode, nmemonic, indir,  args, comment, second_word, second_word_hint) = SELDISASM(val)
#			second_word_hint = None #fixme
			buf2 = "0x%04x\t%06o\t%s%s\t%s" % (i,val,nmemonic, indir, args)
			if comment:
				print("%s\t\t*%s" % (buf2,comment))
			else:
				print("%s" % (buf2))
		else:
			binval = bin(val)[2:].zfill(16)
			buf = "0x%04x\t%06o\t%s\t'%06o\t\t(0b%s) " % (i,val,"DATA",val," ".join([binval[i:i+4] for i in range(0, len(binval), 4)]))
			print(buf,end='')
			if second_word_hint != None:
				hintlst = []
				for  h in second_word_hint[1]:
					t = second_word_hint[0](h, val)
					hintlst.append(second_word_hint[0](h,val))
				print(",".join(hintlst))
			second_word = False
			second_word_hint = None
			first_word = None
		i+=1
