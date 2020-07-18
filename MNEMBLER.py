import struct
import re
import json
import traceback
import sys
from SELOP import *

"""
rel 4
space
oper 4
space
address,index 14
comment 25
"""

"""
'nnnnnn is octal
=nnn decimal


**  LOCATION TO BE FILLED: A double
asterisk (**) indicates the address portion of
the instruction is to be filled in by the object program at run time. This add re s s is set du r -
ing assembly to an absolute add ress of 00000.

The address is presumed to be decimal
unless preceded by an apostrophe (')

ADDRESS ARITHMETIC: Any current
location (*)., symbolic (NAME)., or absolute
(' 1234) address may be joined with a constant,
current locations (*), symbolic (NAME) or
absolute (1234) address by an intervening plus
(+) or minus (-) operator to define an effective
address (NAME+ 4). The above may be extended to more than two operands ' (A - B + 2).


"""




asmlineseq = [5,10,24]
MODE_RELATIVE = True
MODE_ABSOLUTE = False
SEL_INT_MAX = 0xffff


SYMBOLS = {}
EXTERNAL_SYMBOLS = {}
ADDR_MODE = MODE_ABSOLUTE
CUR_ADDRESS = 0
PROGRAM_LISTING = []
CONSTANTS = {}


DIRECT_LOAD = 0
MREF_LOAD = 1
SUB_LOAD = 2
SPECIAL_LOAD = 3

def octprint(val):
	return "%08o" % (val)
	
	



def detectarg(argstring):
	#'003003      #octal
	#+'003003      #octal
	#-'003003      #octal
	#h5A			#hex
	#+h5A			#hex
	#-h5A			#hex
	#*				#current address
	#23.456B10, -B6, 12C0   #FIXED point
	#22.33.44E0, .12345D2	#floating point data
	#''help''		#PHA
	bnext = 0
	sign = 1
	literal = False


	if argstring[bnext] == "-":
		sign = -1
		bnext += 1
	elif argstring[bnext] == "+":
		bnext += 1
		
	if argstring[bnext] == "'": #octal
		bnext += 1
		if argstring[bnext] == "'": #alphanumeric
			bnext += 1
			t = "str"
			lambdaparse = lambda x,y=bnext : str(x[y:-2])
		else:
			t = "oct"
			lambdaparse = lambda x,y=bnext,s=sign : int(x[y:],8) * s
	elif argstring[bnext] == "h": #hex
		bnext += 1
		t = "hex"
		lambdaparse = lambda x,y=bnext,s=sign : int(x[y:],16) * s
	elif argstring[bnext] == "*": #current
		bnext += 1
		if bnext < len(argstring):
			if argstring[bnext] == "*": #"to be filled in at runtime"
				bnext += 1
				t = "ip"
				lambdaparse = lambda x : 0 #"This address is set during assembly to an abso1ute address of 00000."
			else:
				t = "ip"
				lambdaparse = lambda x,y =CUR_ADDRESS,s=sign : y * s
		else:
			t = "ip"
			lambdaparse = lambda x,y =CUR_ADDRESS,s=sign : y * s

	elif argstring[bnext:] in SYMBOLS:
		t = "label"
		lambdaparse = lambda x,y=bnext,s=sign  : SYMBOLS[x[y:]][1] * s
		
	else: #bare number.. still more work
		if "." in argstring: #float or fixed
			if "E" in argstring or "e" in argstring: #float
				t = "float"
				lambdaparse = lambda  x  : float(x)
			else: #fixed
				t = "fixed"
				lambdaparse = lambda  x  : Decimal(x)
		else:#decimal
			t = "dec"
			lambdaparse = lambda  x: int(x)
	return (t,lambdaparse)
	
	
def parsearg(argstring):
	argstring = argstring.strip()
	argparts = re.split("(\+|\-)",argstring)
	total = lambda :0
	mth = lambda x,y : x()+y()
	for i in range(len(argparts)):
		if argparts[i] != "":
			if argparts[i] in ["+","-"]:
				if argparts[i] == "-":
					mth = lambda x,y : x()-y()
				else:
					mth = lambda x,y : x()+y()
			else:
#				if argparts[i][0] == "=":
#					if  argparts[i][0][1:].strip() in CONSTANTS:
#						return lambda x = argparts[i][0][1:].strip(): CONSTANTS[x]
#					else:
#						CONSTANTS[argparts[i][0][1:].strip()] = detectarg(y)[1]()
#						return lambda x = argparts[i][0][1:].strip(): CONSTANTS[x]
						
#						lambdaparse = lambda x,y=argstring[bnext:] : CONSTANTS[detectarg(y)[1]]
#					else:
#						lambdaparse = lambda x,y=argstring[bnext:] : detectarg(y)[1](y)
#					return ("literal",lambdaparse)

			
				t,f = detectarg(argparts[i])
				if t == 'str':
					return lambda x=f : x(argparts[i])
				else:
					total = lambda x=total, y = lambda x=f,y=argparts[i]: x(y), z=mth: z(x, y)
	return total


filename = "boot.asm"
f = open(filename)
ll = f.readlines()
#FIRST PASS
for lnum in range(len(ll)):
	r_flag = False
	x_flag = False
	i_flag = False
	l = ll[lnum]
	l = l.replace("\n","")
	l = list(l)

	if len(l):
		if l[0] == "*":
			continue
		if len(l) > 5:
			l[4] = "\0"
		if len(l) > 10:
			l[9] = "\0"
		if len(l) > 25:
			l.insert(24,"\0")
		(label, op, addridx, comment) = (None,None,None,None)
		
		chunkdat = [x for x in "".join(l).split("\00")]
		
		if len(chunkdat) == 4:
			(label, op, addridx, comment) = chunkdat
		elif  len(chunkdat) == 3:
			(label, op, addridx) = chunkdat
		elif  len(chunkdat) == 2:
			(label, op) = chunkdat
		elif  len(chunkdat) == 1:
			(label,) = chunkdat
		
		if label.strip() == '':
			label = None
		else:
			label = label.strip()
		
		indirect_bit = False
		
		if op != None:
			if op.upper() == "DATA":
				if comment != None:
					addridx += comment
					addridx = addridx.split(" ")[0] #this is a bit of a hack for a special case of data with a comment, but not a long line
				comment = None
			elif op[-1] == "*":
				op = op.replace("*"," ") #indirect instruction
				indirect_bit = True
			op = op.strip()

		if label:
			SYMBOLS[label] = ("int",CUR_ADDRESS)

		if op:
			if op in PSEUDO_OPCODES:
				if op == "REL":
					ADDR_MODE = MODE_RELATIVE
					
				elif op == "ABS":
					ADDR_MODE = MODE_ABSOLUTE
					
				elif op == "ORG":
					r_flag = True
					try:
						PROGRAM_LISTING.append((lnum,op, LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ) | ( LOADER_BITMASKS["R_FLAG"] * r_flag ) , lambda y=addridx:  [parsearg(y)() ] ))
						continue
						
					except Exception as  err:
						print("****\n%s:%d generated the following error\n***" % (filename,lnum+1))
						traceback.print_exc()
						sys.exit(-1)


				elif op in ["***", "ZZZ"]:
					#fixme parse args
					if len(addridx.split(",")) == 1:
						val = addridx
						
					elif len(addridx.split(",")) == 2:
						(addr,idx) = addridx.split(",")
						val = addr
						if int(idx):
							idx = True
							
#					PROGRAM_LISTING.append((lnum,op, (indirect_bit<<14), lambda x,y=val:  [parsearg(y)() | x]))

#					PROGRAM_LISTING.append((lnum,op, (indirect_bit<<14), lambda x,y=val:  [parsearg(y)()]))
					continue



				elif op == "DATA":
					r_flag = True
					for i in addridx.split(","):
						PROGRAM_LISTING.append((lnum,op, LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ), lambda y=i.strip(): [parsearg(y)()] ))
						CUR_ADDRESS += 1
					continue

				elif op == "EQU":
					try:
						SYMBOLS[label] = ("int",parsearg(addridx)()) #first pass only
					except Exception as  err:
						print("****\n%s:%d generated the following error\n***" % (filename,lnum+1))
						traceback.print_exc()
						sys.exit(-1)

					continue
					
				elif op == "DAC": #not right fixme
					idx = False
					x_flag = True
					if len(addridx.split(",")) == 1:
						val = addridx
						
					elif len(addridx.split(",")) == 2:    #fixme
						(addr,idx) = addridx.split(",")
						val = addr
						if int(idx):
							idx = True

					PROGRAM_LISTING.append((lnum,"DATA", LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["R_FLAG"] * r_flag )|( LOADER_BITMASKS["X_FLAG"] * x_flag )|LOADER_BITMASKS["DAC"] ,lambda y=val:[parsearg(y)()]))
					CUR_ADDRESS += 1
					continue
					
				elif op == "EAC": #not right either
					daceac_bit = True
					idx  = False
					x_flag= true
					if len(addridx.split(",")) == 1:
						val = addridx
						 
					elif len(addridx.split(",")) == 2: #fixme too
						(addr,idx) = addridx.split(",")
						val = addr
						if int(idx):
							idx = True

					PROGRAM_LISTING.append((lnum,"DATA", LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["R_FLAG"] * r_flag )|( LOADER_BITMASKS["X_FLAG"] * x_flag )|LOADER_BITMASKS["EAC"] ,lambda y=val:[parsearg(y)()]))
					continue
					
				PROGRAM_LISTING.append((lnum,op, None ,[addridx])) #fail fixme
			
			elif op in MREF_OPCODES:
				if len(addridx.split(",")) == 1:
					addr = addridx
					
				elif len(addridx.split(",")) == 2:
					(addr,idx) = addridx.split(",")
					if int(idx):
						x_flag = True

				PROGRAM_LISTING.append((lnum,op, LOADER_FORMATS[MEMREF_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag )| ( LOADER_BITMASKS["I_FLAG"] * i_flag )| ( LOADER_BITMASKS["R_FLAG"] * r_flag ), lambda y=addr: [parsearg(y)()]))
				CUR_ADDRESS += 1

			elif op in AUGMENTED_OPCODES:
				
				shift_count = 0
				if addridx and addridx.strip() != "":
					try:
						shift_count = parsearg(addridx)()
					except Exception as  err:
						print("****\n%s:%d generated the following error\n***" % (filename,lnum+1))
						traceback.print_exc()
						sys.exit(-1)

				opcode = (AUGMENTED_OPCODES[op][0] << 12) | (shift_count << 6) | AUGMENTED_OPCODES[op][1]
				
				PROGRAM_LISTING.append((lnum,"DATA", LOADER_FORMATS[DIRECT_LOAD][1], lambda y=opcode: [y]))
				CUR_ADDRESS += 1
				
			elif op in IO_OPCODES:
				x_bit = False
				map_bit = False
				augment_code = 0
				wait_bit = False
				merge_bit = False
				unit = 0
				
				if len(addridx.split(",")) == 2:
					(unit, wait) = addridx.split(",")
					if wait == "W":
						wait_bit = True
				elif  len(addridx.split(",")) == 3:
					(unit, wait, merge) = addridx.split(",")
					if merge == "R":
						merge_bit = True
					if wait == "W":
						wait_bit = True
						

				if IO_OPCODES[op][1]:
					opcode = (IO_OPCODES[op][0] << 6) | (merge_bit << 11) | (indirect_bit << 10) | (map_bit << 9) | (wait_bit << 6)
				else:
					opcode = (IO_OPCODES[op][0] << 6) | (wait_bit << 6)
				PROGRAM_LISTING.append((lnum,"DATA", LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ),lambda x=opcode, y=unit:[parsearg(y)()|x]))

				CUR_ADDRESS += 1

			elif op in INT_OPCODES:
				merge_bit = 0
				augment_code = 0
				if addridx:
					try:
						augment_code = parsearg(addridx)
					except Exception as  err:
						print("****\%s:%d generated the following error" % (filename,lnum+1))
						traceback.print_exc()
						sys.exit(-1)

				opcode = (INT_OPCODES[op] << 12) | augment_code
				PROGRAM_LISTING.append((lnum,"DATA", LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ),lambda x=opcode, y=augment_code:[parsearg(y)()|x]))

				CUR_ADDRESS += 1

					

			else:
				print("unhandled opcode [%s] on %s:%d in first pass.. you should fix that.. fatal" % (op,filename,lnum+1))
				exit()



	
print("assigning constants to end of program memory")
o = 0
for c in CONSTANTS: #assign literals to memory at the end of the program
	CONSTANTS[c] = CUR_ADDRESS + o
	o+=1;
	PROGRAM_LISTING.append((0,"DATA", c ,lambda x: [x]))

for l in PROGRAM_LISTING:
	print("%08o\t%s\t\t\t" % ((l[2]| l[-1]()[0] ),ll[l[0]].strip()), l,l[-1]())


##second pass
#PROGRAM = {0:[]}
#CUR_ADDRESS = 0
#CUR_ORG = 0
#for lnum, op,opcode,finfunc in PROGRAM_LISTING:
#	if op in PSEUDO_OPCODES:
#		if op == "REL":
#			ADDR_MODE = MODE_RELATIVE
#
#		elif op == "ABS":
#			ADDR_MODE = MODE_ABSOLUTE
#
#		elif op == "MOR": #we dont need to actually pause
#			pass
#
#		elif op in ["***", "zzz"]:
#			for b in finfunc(opcode):
#				PROGRAM[CUR_ORG].append((lnum,CUR_ADDRESS,b))
#				CUR_ADDRESS += 1
#
#		elif op == "LIST": #list program output
#			pass
#
#		elif op == "NOLS": #nolist program output
#			pass
#
#		elif op == "NAME": #subroutine name
#			pass
#
#		elif op == "ORG":
#			addr = parsearg(finfunc[0])()
#			if ADDR_MODE == MODE_ABSOLUTE:
#				CUR_ORG = addr
#			elif ADDR_MODE == MODE_RELATIVE:
#				CUR_ORG += addr
#
#			CUR_ADDRESS  = CUR_ORG
#			PROGRAM[CUR_ORG] = []
#
#		elif op in ["DAC","DATA","EAC"]:
#			for b in finfunc(opcode):
#				PROGRAM[CUR_ORG].append((lnum,CUR_ADDRESS,b))
#				CUR_ADDRESS += 1
#
#	elif op in MREF_OPCODES or op in AUGMENTED_OPCODES or op in IO_OPCODES or op in INT_OPCODES:
#		try:
#			for b in finfunc(opcode):
#				PROGRAM[CUR_ORG].append((lnum,CUR_ADDRESS,b))
#				CUR_ADDRESS += 1
#		except Exception as  err:
#			print("%s:%d generated the following error" % (filename,lnum+1))
#			traceback.print_exc()
#			sys.exit()
#
##print(len(PROGRAM))
#outbuff = []
#print("writing text")
#fn = "%s.S"  % ".".join(filename.split(".")[:-1])
#f = open(fn, "w")
#for o,pgm in PROGRAM.items():
#	if len(pgm):
#		outbuff.append("load offset: 0x%04x [0o%06o]" %  (o,o))
#		for o in range(len(pgm)):
#			outbuff.append("\tLine#: %04d\t Addr: %s\tOCT: %s\tHEX: 0x%04x" % (pgm[o][0], pgm[o][1], octprint(pgm[o][2]),pgm[o][2] & 0xffff))
#
#for l in outbuff:
#	print("%s" % l)
##	f.write("%s\n" % l)
##f.close()
#
#print("writing binary")
##fn = "%s.bin"  % ".".join(filename.split(".")[:-1])
##f = open(fn, "w")
##for o,pgm in PROGRAM.items():
##	print(pgm)
##	f.write((pgm[o][2] >> 8) &0xFF)
##	f.write(pgm[o][2] & 0xFF)
##f.close()
#
#
#
#fn = "%s.sym"  % ".".join(filename.split(".")[:-1])
#print("writing symbols %s" % fn)
#f = open(fn, "w")
#f.write(json.dumps(SYMBOLS))
#f.close()
