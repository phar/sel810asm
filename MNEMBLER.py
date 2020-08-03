import struct
import re
import json
import traceback
import sys
from SELOP import *
from util import *


MODE_RELATIVE = True
MODE_ABSOLUTE = False
SEL_INT_MAX = 0xffff


SYMBOLS = {}
EXTERNAL_SYMBOLS = {}
CONSTANTS = {}
EXPORTS = {}
MACROS = {}


DIRECT_LOAD = 0
MREF_LOAD = 1
SUB_LOAD = 2
SPECIAL_LOAD = 3

	
NOT_FORBIDDEN_CHARS = [ord(x) for x in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\r\n\b\x08[\\]^_ !\"#$%&'()*+,-./:;<=>?")]
FORBIDDEN_CHARS = []
for c in range(0,0xff):
	if c not in NOT_FORBIDDEN_CHARS:
		FORBIDDEN_CHARS.append(c)


def decompose_asm(l):
	l = l.replace("\n","")
	l = list(l)
	ismacroinst = False
			
	if len(l):
		if l[0] == "*":
			return (None,ismacroinst,None,False,None,None)
		if len(l) > 5:
			if l[4] == "M":
				ismacroinst = True
			l[4] = "\0"
			
		if len(l) > 10:
			l[9] = "\0"
			
		in_quotes = False
		qc = 0
		for i in range(0, len(l)): #this matches the manual much better, doesnt actually mention quotes
			if in_quotes:
				if l[i] == "'":
					qc -= 1
				if qc == 0:
					in_quotes = False
			else:
				if l[i] == "'":
					qc += 1
				if qc == 2:
					in_quotes = True
					
			if in_quotes == 0 and l[i] == " " and (i > 13):
				l[i] = "\0"
				break
					
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

		if comment:
			comment = comment.lstrip()

		indirect_bit = False
		
		if op != None:
			op = op.strip()
			if op.strip() != "":
				if op[-1] == "*":
					op = op[:-1]     #indirect instruction
					indirect_bit = True
		if addridx:
			addridx = addridx.strip()
		return (label,ismacroinst,op, indirect_bit, addridx, comment)

def get_unique_label():
	n = 0
	s = "_%d" % n
	while s in SYMBOLS: #hacky but closer to what the actuall assembler seemed to do
		n = n+1
		s = "_%d" % n
		if n > 999:
			raise ValueError
	return s
	
def asm_pass_1(filename,base_address=0):
	program_listing = []
	cur_address = base_address
	supress_output = False
	in_macro_name = None
	ll = load_file(filename)
	lnum = 0
	addr_mode = MODE_ABSOLUTE
	
	while(len(ll[lnum:])):
		r_flag = False
		x_flag = False
		i_flag = False
		handled = False
		current_offset =0
		l = ll[lnum]
		lnum += 1
		args = []
		
		if 1 in [c in [ord(x) for x in l] for c in FORBIDDEN_CHARS]:
			print("illegal caracters on line %s:%d fatal" % (filename,lnum))
			exit()
		
		if l.strip() != "":
			(label,ismacroinst,op, indirect_bit, addridx, comment) = decompose_asm(l)
			if op is not None or label is not None:
				if in_macro_name != None:
					if op == "EMAC":
						in_macro_name = None
						continue
					else:
						MACROS[in_macro_name].append(l)
				else:
					
					if ismacroinst:
						if op in MACROS:
							c = 0
							n = 0
							ulbl = get_unique_label()
							local_labels = {}
							
							if addridx != None:
								params = addridx.split(",")
							else:
								params = []
								
							for ml in MACROS[op]:
								(mlabel,mismacroinst,mop,mindirect_bit, maddridx, mcomment) = decompose_asm(ml)

								if mlabel is not None:
									if mlabel[0] == "@":
										local_labels[mlabel.strip()] = get_unique_label()
								
								if "@" in ml:
									m = re.findall("(@\d+)",ml)
									for s in m:
										ml = ml.replace(s, local_labels[s])

								if "#" in ml:
									m = re.findall("(#\d+)",ml)
									for s in m:
										ml = ml.replace(s, params[int(s[1:])-1])

								ll.insert(lnum+c,ml)
								c = c + 1
						else:
							print("macro %s not found" % op)
						continue
					else:
						if label:
							SYMBOLS[label] = ("int",cur_address)
					
					if op:
						if op in PSEUDO_OPCODES:
							if op == "REL":
								addr_mode = MODE_RELATIVE
								handled = True #fixme, this will eventually have consequences
								continue

							elif op == "ABS":
								addr_mode = MODE_ABSOLUTE
								continue
								
							elif op == "BSS":
								args = addridx.split(" ")
								#FIXME, arg[1] should be an optional addres.. but.. i dont think i handle it at all
								#am i expected to emit an ORG?
								fooargs.append(args[0])
								if len(args) > 1:
									fooargs.append(args[1])
								if comment:
									fooargs.append("#%s"%comment)

								for d in range(0,parsearg(cur_address,SYMBOLS, args[0])(),2):
									program_listing.append((lnum,cur_address,op,indirect_bit,fooargs, LOADER_FORMATS[DIRECT_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ), lambda x=0:[x],supress_output))
									fooargs = []
									cur_address += 1
								handled = True
								continue

							elif op == "BES":
								args = addridx.split(" ")
								#FIXME, arg[1] should be an optional addres.. but.. i dont think i handle it at all
								fooargs.append(args[0])
								if len(args) > 1:
									fooargs.append(args[1])
								if comment:
									fooargs.append("#%s"%comment)

								for d in range(0,parsearg(cur_address,SYMBOLS, args[0])(),2):
									program_listing.append((lnum,cur_address,op,indirect_bit,fooargs, LOADER_FORMATS[DIRECT_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ), lambda x=0:[x],supress_output))
									SYMBOLS[label] = ("int",cur_address) #adjust the label to point to the end of the block
									fooargs = []
									cur_address += 1
								handled = True
								continue

							elif op == "MACR":
								in_macro_name = label
								MACROS[in_macro_name] = []
								handled = True
								continue
								
							elif op == "END":
								if comment:
									args.append("#%s"%comment)
								program_listing.append((lnum,cur_address,op,indirect_bit,args,0xe20000 , lambda : [0],supress_output))
								handled = True
								cur_address += 1
								continue
								
							elif op == "NAME":
								#program_listing.append((lnum,cur_address,op,0xe20000 , lambda : [0]),supress_output)
								continue
								
							elif op == "NOLS":
								supress_output = True
								handled = True
								continue
								
							elif op == "MOR":
								#lol
								handled = True
								continue
								
							elif op == "LIST":
								supress_output = False
								handled = True
								continue
								
							elif op == "ORG":
								r_flag = True
								try:
									cur_address = parsearg(cur_address,SYMBOLS,addridx)()
									args.append("'%06o" % cur_address)
									if comment:
										args.append("#%s"%comment)
									program_listing.append((lnum,cur_address,op,indirect_bit,args, LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ) | ( LOADER_BITMASKS["R_FLAG"] * r_flag ) , lambda x=cur_address, y=addridx:  [parsearg(x,SYMBOLS,y)() ],supress_output))
									handled = True
									continue
									
								except Exception as  err:
									print("****\n%s:%d generated the following error\n***" % (filename,lnum))
									traceback.print_exc()
									sys.exit(-1)

							elif op in ["***", "ZZZ"]:
								if len(addridx.split(",")) == 1:
									val = addridx
									
								elif len(addridx.split(",")) == 2:
									(addr,idx) = addridx.split(",")
									val = addr
									args.append("'%06o" % val)
									
									if int(idx):
										idx = True
										args.append("1")
								if comment:
									args.append("#%s"%comment)
								program_listing.append((lnum,cur_address,op,indirect_bit,args, (indirect_bit<<14), lambda x=cur_address,y=val: [parsearg(x,SYMBOLS,y)()],supress_output))
								handled = True
								continue

							elif op == "DATA":
								r_flag = True

								if "," not in addridx or addridx[:2] == "''":
									lst = [addridx]
								else:
									lst = addridx.split(",")
									
								for li in lst:
									data = parsearg(cur_address,SYMBOLS,li)()
										
									if isinstance(data,list):
										foobuff = []
										
										if comment:
											foobuff.append("#%s"%li + " " + comment)
										else:
											foobuff.append("#%s"%li + " ")

										for d in range(0,len(data),2):
											try:
												r =  (data[d] << 8) | (data[d+1])
											except IndexError:
												r = data[d]
											program_listing.append((lnum,cur_address,op,indirect_bit,["'%06o" % r]+foobuff, LOADER_FORMATS[DIRECT_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ), lambda x=r:[x],supress_output))
											cur_address += 1
											foobuff = []

									else:
										args.append("'%06o" % data)
										if comment:
											args.append("#%s"%comment)
										program_listing.append((lnum,cur_address,op,indirect_bit,args,LOADER_FORMATS[DIRECT_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ), lambda x=data:[x],supress_output))
										cur_address += 1
									
								handled = True
								continue

							elif op == "EQU":
								try:
									args.append("'%06o" % addridx)
									SYMBOLS[label] = ("int",parsearg(cur_address, SYMBOLS, addridx)()) #first pass only
								except Exception as  err:
									print("****\n%s:%d generated the following error\n***" % (filename,lnum))
									traceback.print_exc()
									sys.exit(-1)
								continue
								
							elif op == "DAC": #not right fixme
								idx = False
								x_flag = True
								
								if len(addridx.split(",")) == 1:
									val = addridx
									args.append("'%06o" % val)
									
								elif len(addridx.split(",")) == 2:    #fixme
									(addr,idx) = addridx.split(",")
									val = addr
									args.append("'%06o" % val)
									if int(idx):
										idx = True
										args.append("1")
								if comment:
									args.append("#%s"%comment)
								program_listing.append((lnum,cur_address,"DAC",indirect_bit, args, LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["R_FLAG"] * r_flag )|( LOADER_BITMASKS["X_FLAG"] * x_flag )|LOADER_BITMASKS["DAC"] ,lambda x=cur_address,y=val:[parsearg(x,SYMBOLS,y)()],supress_output))
								handled = True
								cur_address += 1
								continue
								
							elif op == "EAC": #not right either
								daceac_bit = True
								idx  = False
								x_flag= true
								if len(addridx.split(",")) == 1:
									val = addridx
									args.append("'%06o" % val)
									 
								elif len(addridx.split(",")) == 2: #fixme too
									(addr,idx) = addridx.split(",")
									val = addr
									args.append("'%06o" % val)
									if int(idx):
										idx = True
										args.append("1")
										
								if comment:
									args.append("#%s"%comment)
								program_listing.append((lnum,cur_address,"EAC",args, LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["R_FLAG"] * r_flag )|( LOADER_BITMASKS["X_FLAG"] * x_flag )|LOADER_BITMASKS["EAC"] ,lambda x=cur_address,y=val:[parsearg(x,SYMBOLS,y)()]),supress_output)
								handled = True
								continue
								
						elif op in MREF_OPCODES:
							addr = addridx
							if indirect_bit:
								i_flag = True
								
							if addr[0] == "=":
								x_flag = True
								args.append(addr)
								if comment:
									args.append("#%s"%comment)
								program_listing.append((lnum,cur_address,op,indirect_bit,args,(MREF_OPCODES[op] << 17 ) | LOADER_FORMATS[LITERAL_LOAD][1]| ( LOADER_BITMASKS["X_FLAG"] * x_flag )| ( LOADER_BITMASKS["R_FLAG"] * r_flag ), lambda x=cur_address,y=addr[1:]: [parsearg(x,SYMBOLS,y)()],supress_output))
								handled = True
							else:
								r_flag = True
								if len(addridx.split(",")) == 1:
									addr = addridx
									args.append(addr)
									
								elif len(addridx.split(",")) == 2:
									(addr,idx) = addridx.split(",")
									args.append(addr)
									if int(idx):
										x_flag = True
										args.append("1")
								if comment:
									args.append("#%s"%comment)
								program_listing.append((lnum,cur_address,op,indirect_bit,args, (MREF_OPCODES[op] << 17 ) | LOADER_FORMATS[MEMREF_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag )| ( LOADER_BITMASKS["I_FLAG"] * i_flag )| ( LOADER_BITMASKS["R_FLAG"] * r_flag ), lambda x=cur_address,y=addr: [parsearg(x,SYMBOLS,y)()],supress_output))
								handled = True
							cur_address += 1

						elif op in AUGMENTED_OPCODES:
							shift_count = 0
							if addridx and addridx.strip() != "":
								try:
									shift_count = parsearg(cur_address,SYMBOLS,addridx)()
									if shift_count:
										args.append("'%o" % shift_count)
										
								except Exception as  err:
									print("****\n%s:%d generated the following error\n***" % (filename,lnum))
									traceback.print_exc()
									sys.exit(-1)

							opcode = (AUGMENTED_OPCODES[op][0] << 12) | (shift_count << 6) | AUGMENTED_OPCODES[op][1]
							if comment:
								args.append("#%s"%comment)
							program_listing.append((lnum,cur_address,op,indirect_bit,args, LOADER_FORMATS[DIRECT_LOAD][1], lambda y=opcode: [y],supress_output))
							handled = True
							cur_address += 1
							
						elif op in IO_OPCODES:
							x_bit = False
							map_bit = False
							augment_code = 0
							wait_bit = False
							unit = addridx
							index_bit = 0
							
							if len(addridx.split(",")) == 2:
								(unit, wait) = addridx.split(",")
								args.append(unit)
								if wait == "W":
									wait_bit = True
									args.append("W")
									
							elif  len(addridx.split(",")) == 3:
								(unit, wait, index) = addridx.split(",")
								args.append("'%o" % unit)

								if index == "1":
									index_bit = True
									args.append("1")

								if wait == "W":
									wait_bit = True
									args.append("W")

							opcode = (IO_OPCODES[op][0] << 12) | (index_bit << 11) | (indirect_bit << 10) | (map_bit << 9) | (wait_bit << 6) | (IO_OPCODES[op][1] << 7)
							if comment:
								args.append("#%s"%comment)
							program_listing.append((lnum,cur_address,op,indirect_bit,args, LOADER_FORMATS[DIRECT_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ) | opcode,lambda x=cur_address,y=unit:[parsearg(x,SYMBOLS,y)()],supress_output))
							handled = True
							cur_address += 1

						elif op in INT_OPCODES:
							augment_code = 0
							if addridx:
								try:
									augment_code = parsearg(SYMBOLS,addridx) #fixme borken
								except Exception as  err:
									print("****\%s:%d generated the following error" % (filename,lnum))
									traceback.print_exc()
									sys.exit(-1)

							opcode = (INT_OPCODES[op] << 12) | augment_code
							if comment:
								args.append("#%s"%comment)
							program_listing.append((lnum,cur_address,op,indirect_bit,args, LOADER_FORMATS[LITERAL_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ),lambda x=opcode, y=augment_code, z=cur_address:[parsearg(z,SYMBOLS, y)()|x],supress_output))
							args.append("'%06o" % opcode)

							handled = True
							cur_address += 1
							
						else:
							print("unhandled opcode [%s] on %s:%d in first pass.. you should fix that.. fatal" % (op,filename,lnum))
							exit()

						if handled == False:
							program_listing.append((lnum,"ERROR",None,None,None,None,supress_output))
	return (addr_mode,program_listing)
	
	
def load_file(filename):
	f = open(filename)
	ll = f.readlines()
	return ll

filename = sys.argv[1]

#FIRST PASS
(addr_mode,program_listing) = asm_pass_1(filename)

fn = "%s.sym"  % ".".join(filename.split(".")[:-1])
print("writing symbols %s" % fn)
f = open(fn, "w")
f.write(json.dumps(SYMBOLS))
f.close()




print("creating relocatable binary")
relocatable_file = []
for (lnum,cur_address,op,indirect_bit,args,oparg,oparg_calc,supress) in program_listing:
	if oparg != None:
		for v in oparg_calc():
			label = ""
			for s,a in SYMBOLS.items():
				if a[1] == cur_address:
					label = s

			if v < 0:
				val = oparg | ((~abs(v) + 1)  & 0xffff)#its a 16 bit value so to fix the sign bit
			else:
				val = oparg | v
				
			if indirect_bit:
				indir = "*"
			else:
				indir = " "
				
			if not label:
				label = "    "
			else:
				label = label.ljust(4," ")
				
			if len(args) and args[-1][0] == "#":
				testbuff = "%s %s%s %s" % (label,op, indir, ",".join(args[:-1]))
				buf = "*"+args[-1][1:]
				testbuff += buf.rjust(27 + (len(buf) - len(testbuff))," ")
			else:
				testbuff = "%s %s%s %s" % (label,op, indir, ",".join(args))
			outline  = "%04x\t%08o\t%s\t\t\t" % (cur_address,val,testbuff)
			if not supress:
				print(outline)
			relocatable_file.append((val,outline))
	else:
		relocatable_file.append((0x0,"ERROR!"))
		print(l)
f.close()



if addr_mode == MODE_RELATIVE:
	print("writing binary")
	fn = "%s.obj"  % ".".join(filename.split(".")[:-1])
	f = open(fn, "wb")
	for val,line in relocatable_file:
		f.write(struct.pack("3B", (val & 0xff0000) >> 16, (val & 0xff00) >> 8,(val & 0xff) ))
	f.close()
else:
	print("uh.. we dont really support absolute mode right now")
