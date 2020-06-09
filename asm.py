import struct
import re

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

PSEUDO_OPCODES = {"ABS":(),"REL":(),"ORG":(),"EQU":(),"DAC":(),"EAC":(),"DATA":(), "END":()}

BASE_OPCODES = {"LAA":0o1,"LBA":0o2,"STA":0o3,"STB":0o4,"AMA":0o5,"SMA":0o6,"MPY":0o7,"DIV":0o10,"BRU":0o11,"SPB":0o12,"IMS":0o14,"CMA":0o15,"AMB":0o16}

AUGMENTED_OPCODES = { "ABA":(0,0o27),"ASC":(0,0o20),"CLA":(0,0o3), "CNS":(0,0o34),"CSB":(0,0o7), "FLA":(0,0o17),"FLL":(0,0o13),"FRA":(0,0o12),
					  "FRL":(0,0o14),"HLT":(0,0o0), "IAB":(0,0o6), "IBS":(0,0o26),"ISX":(0,0o51),"LCS":(0,0o31),"LIX":(0,0o45),"LOB":(0,0o36),
					  "LSA":(0,0o11),"LSL":(0,0o16),"NEG":(0,0o2), "NOP":(0,0o33),"OBA":(0,0o30),"OVS":(0,0o37),"RNA":(0,0o1), "RSA":(0,0o10),
					  "RSL":(0,0o15),"SAN":(0,0o23),"SAP":(0,0o24),"SAS":(0,0o21),"SAZ":(0,0o22),"SNO":(0,0o32),"SOF":(0,0o25),"STX":(0,0o44),
					  "STB":(0,0o50),"TAB":(0,0o5), "TAZ":(0,0o52),"TBA":(0,0o4), "TBP":(0,0o40),"TBV":(0,0o42),"TOI":(0,0o35),"TPB":(0,0o41),
					  "TVB":(0,0o43),"TXA":(0,0o53),"XPB":(0,0o47),"XPX":(0,0o46)}
					  
IO_OPCODES = {"CEU":(0o13,0,1,1,0o0),"MIP":(0o13,0,1,1,0o6),"MOP":(0o13,0,1,1,4),"TEU":(0o13,0,1,1,0o2)}

INT_OPCODES ={"PID":(0o130601),"PIE":(0o130600)}

f = open("boot.asm")
ll = f.readlines()

asmlineseq = [5,10,24]

SYMBOLS = {}
EXTERNAL_SYMBOLS = {}
MODE_RELATIVE = 0
MODE_ABSOLUTE = 1

ADDR_MODE = MODE_ABSOLUTE

CUR_ADDRESS = 0
PROGRAM_LISTING = []

def octprint(val,pad=6):
	return '0o' + oct(val)[2:].zfill(pad)


def detectarg(argstring):
	argstring = argstring.strip()
	bnext = 0
	sign = 1
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
	argparts = re.split("(\+|\-)",argstring)
	total = lambda :0
	mth = lambda x,y : x()+y()
	for i in range(len(argparts)):
		if argparts[i] != "":
			if argparts[i] in ["+","-"]:
				if argparts[i] == "-":
#					print("minus")
					mth = lambda x,y : x()-y()
				else:
#					print("plus")
					mth = lambda x,y : x()+y()
			else:
				t,f = detectarg(argparts[i])
#				print(f(argparts[i]))
				if t == 'str':
					return lambda x=f : x(argparts[i])
				else:
					total = lambda x=total, y = lambda x=f,y=argparts[i] : x(y): mth(x, y)
	return total


#FIRST PASS
for l in ll:
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
		
		if label == '':
			label = None
			
		if op != None:
			if op.upper() == "DATA":
				if comment != None:
					addridx += comment
				comment = None
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
					addr = parsearg(addridx)
					if ADDR_MODE == MODE_ABSOLUTE:
						CUR_ADDRESS  = addr()
					elif ADDR_MODE == MODE_RELATIVE:
						CUR_ADDRESS  += addr()

				elif op == "DATA":
					vallist = []
					print(addridx)
					for i in addridx.split(","):
						vallist.append(parsearg(i.strip()))
						CUR_ADDRESS += 1
					PROGRAM_LISTING.append((op, 0x0,vallist))
					continue

				elif op == "EQU":
					val = parsearg(addridx)()
					SYMBOLS[label] = ("int",val)
					continue
				PROGRAM_LISTING.append((op, None ,addridx))

			
			elif op in BASE_OPCODES:
				index_bit = 0
				indirect_bit = 0
				map_bit = 0
				
				taddridxparts = addridx.split(",")
				addridxparts = []
				for p in taddridxparts:
					addridxparts.append(parsearg(p))

				opcode = (BASE_OPCODES[op] << 12) | (index_bit << 11) | (indirect_bit << 10) | (map_bit << 9)
				PROGRAM_LISTING.append((op, opcode,addridxparts))
				CUR_ADDRESS += 1
				
			elif op in AUGMENTED_OPCODES:
				shifts = 0
				opcode = (AUGMENTED_OPCODES[op][0] << 12) | (shifts << 6) |  AUGMENTED_OPCODES[op][1]
				PROGRAM_LISTING.append((op, opcode,lambda x:x))
				CUR_ADDRESS += 1
				
			elif op in IO_OPCODES:
				pass
			elif op in INT_OPCODES:
				PROGRAM_LISTING.append((op, opcode,lambda x:x))
				CUR_ADDRESS += 1
			else:
				print("unhandled %s" % chunkdat)
				

print(PROGRAM_LISTING)
#second pass
PROGRAM = []
CUR_ADDRESS = 0
for op,opcode,finfunc in PROGRAM_LISTING:
	if op in PSEUDO_OPCODES:
		if op == "REL":
			ADDR_MODE = MODE_RELATIVE
			
		elif op == "ABS":
			ADDR_MODE = MODE_ABSOLUTE

		elif op == "ORG":
			addr = parsearg(finfunc)()
			if ADDR_MODE == MODE_ABSOLUTE:
				CUR_ADDRESS  = addr
			elif ADDR_MODE == MODE_RELATIVE:
				CUR_ADDRESS  += addr
				
		elif op == "DATA":
			print("moo",finfunc)
			for b in finfunc:
				PROGRAM.append(b())
				CUR_ADDRESS += 1
			
	elif op in BASE_OPCODES:
		vals = [x() for x in finfunc]
#		PROGRAM.append(vals)#fixme
	
		PROGRAM.append(opcode)#fixme
		CUR_ADDRESS += 1
		
	elif op in AUGMENTED_OPCODES:
		PROGRAM.append(finfunc(opcode))
		print("%s %04x %s 0x%04x" % (op, CUR_ADDRESS,octprint(PROGRAM[-1]),PROGRAM[-1]))
		CUR_ADDRESS += 1
		
	elif op in IO_OPCODES:
		pass
		
	elif op in INT_OPCODES:
		PROGRAM.append(finfunc(opcode))
		print("%s %04x %s 0x%04x" % (op, CUR_ADDRESS,octprint(PROGRAM[-1]),PROGRAM[-1]))
		CUR_ADDRESS += 1

#print(PROGRAM)
for o in range(len(PROGRAM)):
	print("%s\t%s\t0x%06x" % (o, octprint(PROGRAM[o]),PROGRAM[o]))

# pseudo "ABS","REL","ORG","EQU", "DAC", "EAC","DATA"
