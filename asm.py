import struct

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

BASE_OPCODES = {"LAA":1,"LBA":2,"STA":3,"STB":4,"AMA":5,"SMA":6,"MPY":7,"DIV":10,"BRU":11,"SPB":12,"IMS":14,"CMA":15,"AMB":16}

AUGMENTED_OPCODES = { "ABA":(0,27),"ASC":(0,20),"CLA":(0,3), "CNS":(0,34),"CSB":(0,7), "FLA":(0,17),"FLL":(0,13),"FRA":(0,12),
					  "FRL":(0,14),"HLT":(0,0), "IAB":(0,6), "IBS":(0,26),"ISX":(0,51),"LCS":(0,31),"LIX":(0,45),"LOB":(0,36),
					  "LSA":(0,11),"LSL":(0,16),"NEG":(0,2), "NOP":(0,33),"OBA":(0,30),"OVS":(0,37),"RNA":(0,1), "RSA":(0,10),
					  "RSL":(0,15),"SAN":(0,23),"SAP":(0,24),"SAS":(0,21),"SAZ":(0,22),"SNO":(0,32),"SOF":(0,25),"STX":(0,44),
					  "STB":(0,50),"TAB":(0,5), "TAZ":(0,52),"TBA":(0,4), "TBP":(0,40),"TBV":(0,42),"TOI":(0,35),"TPB":(0,41),
					  "TVB":(0,43),"TXA":(0,53),"XPB":(0,47),"XPX":(0,46)}

f = open("boot.asm")
ll = f.readlines()

asmlineseq = [5,10,24]

LABELS = {}
MODE_RELATIVE = 0
MODE_ABSOLUTE = 1

ADDR_MODE = MODE_ABSOLUTE

CUR_ADDRESS = 0
PROGRAM_LISTING = []

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
			LABELS[label] = CUR_ADDRESS

		if op:
			if op in PSEUDO_OPCODES:
				if op == "REL":
					ADDR_MODE = MODE_RELATIVE
					
				elif op == "ABS":
					ADDR_MODE = MODE_ABSOLUTE
					
				elif op == "ORG":
					if addridx[0] == "'": #octal
						addr = int(addridx[1:], 8)
					elif addridx[0] == "=": #dec
						addr  = int(addridx[1:], 8)
						
					if ADDR_MODE == MODE_ABSOLUTE:
						CUR_ADDRESS  = addr
					elif ADDR_MODE == MODE_RELATIVE:
						CUR_ADDRESS  += addr

				elif op == "DATA":
					if addridx[0] == "'": #octal
						val = int(addridx[1:], 8)
						CUR_ADDRESS += 1
						PROGRAM_LISTING.append((op, 0x0,val))

				elif op == "EQU":
					if addridx[0] == "'": #octal
						val = int(addridx[1:], 8)
					LABELS[label] = val
					
				PROGRAM_LISTING.append((op, None ,addridx))

			
			elif op in BASE_OPCODES:
				index_bit = 0
				indirect_bit = 0
				map_bit = 0
				
				addr =  None #just here to cause  errors
				if addridx[0] == "'": #octal
					addrfunc = lambda x,y=addridx[1:] : (x | int(y, 8))
					
				elif addridx[0] == "=": #dec
					addrfunc  = lambda x,y=addridx[1:] : (x | int(y, 8))
					
				elif addridx[0] == "$": #external symbolic address
					print(chunkdat)

				elif addridx[0] == "*": #current location
					print(chunkdat)
					addrfunc = lambda x,y=CUR_ADDRESS : x | y
				else:
					addrfunc =  lambda x,y=addridx : x | LABELS[y]

				opcode = (BASE_OPCODES[op] << 12) | (index_bit << 11) | (indirect_bit << 10) | (map_bit << 9)
				PROGRAM_LISTING.append((op, opcode,addrfunc))
				CUR_ADDRESS += 1
				
			elif op in AUGMENTED_OPCODES:
				shifts = 0
				opcode = (AUGMENTED_OPCODES[op][0] << 12) | (shifts << 6) |  AUGMENTED_OPCODES[op][1]
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
			if finfunc[0] == "'": #octal
				addr = int(finfunc[1:], 8)
			elif finfunc[0] == "=": #dec
				addr  = int(finfunc[1:], 8)
				
			if ADDR_MODE == MODE_ABSOLUTE:
				CUR_ADDRESS  = addr
			elif ADDR_MODE == MODE_RELATIVE:
				CUR_ADDRESS  += addr
		elif op == "DATA":
			PROGRAM.append(finfunc)
			
	if op in BASE_OPCODES:
		PROGRAM.append(finfunc(opcode))
		print("%s %04x %s 0x%04x" % (op, CUR_ADDRESS,oct(PROGRAM[-1]),PROGRAM[-1]))
		CUR_ADDRESS += 1
		
	elif op in AUGMENTED_OPCODES:
		PROGRAM.append(finfunc(opcode))
		print("%s %04x %s 0x%04x" % (op, CUR_ADDRESS,oct(PROGRAM[-1]),PROGRAM[-1]))
		CUR_ADDRESS += 1


print(PROGRAM)
# pseudo "ABS","REL","ORG","EQU", "DAC", "EAC","DATA"
