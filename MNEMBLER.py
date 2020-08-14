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


def pack_data(type, data):
	wordlist  = []

	if type in ["oct","hex","dec"]:
		if data < 0:
			wordlist.append((~abs(data) + 1)  & 0xffff) #its a 16 bit value so to fix the sign bit
		else:
			wordlist.append(data)

	elif type == 'str':
		for d in range(0,len(data),2):
			try:
				r = ((data[d] | 0x80) << 8) | ((data[d+1] | 0x80)) # plus ASR33 bit
			except IndexError:
				r = (data[d] | 0x80)  << 8
				
			wordlist.append(r)
			
	elif type == 'float': #2 words  i cant figure out how to pack these
		wordlist.append(0)
		wordlist.append(0)

	elif type == 'double_float': #3 words
		wordlist.append(0)
		wordlist.append(0)
		wordlist.append(0)

	elif type == 'fixed_double':  #this is a bit of a guess about how to pack these, the manual isnt explicit, so i assume scientific notation
		wordlist.append((data >> 16) & 0xffff)
		wordlist.append(data & 0xffff)
		
	elif type == 'fixed_single':#this is a bit of a guess about how to pack these, the manual isnt explicit, so i assume scientific notation
		wordlist.append(data & 0xffff)

	elif type == 'dec':
		wordlist.append(data & SEL_INT_MAX)

	else:
		pass #fixme
	
	return wordlist

	
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
#							if label not in SYMBOLS:
								SYMBOLS[label] = ("int",cur_address)
#							else:
#								print(SYMBOLS)
#								print("****\n%s:%d duplicate symbol (%s) definition\n***" % (filename,lnum,label))
#								sys.exit(-1)
					if op:
						if op in PSEUDO_OPCODES:
							if op == "REL":
								addr_mode = MODE_RELATIVE
								handled = True #fixme, this will eventually have consequences
								continue

							elif op == "ABS":
								addr_mode = MODE_ABSOLUTE
								continue
								
							elif op == "MAP":
								print("oh jeeze, your trying to use an option i never really figured out, im just going to go ahead and bow out now")
								sys.exit(-1)
								continue
													
							elif op == "BSS":
								args = addridx.split(" ")
								#FIXME, arg[1] should be an optional addres.. but.. i dont think i handle it at all
								#am i expected to emit an ORG?
								fooargs = [args[0]]
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
								fooargs = [args[0]]
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

							elif op == "***":
								if comment:
									args.append("#%s"%comment)
									
								program_listing.append((lnum,cur_address,op,indirect_bit,args, 0, lambda x=cur_address,y=val: [0],supress_output))
								handled = True
								
							elif op == "ZZZ":
								if len(addridx.split(",")) == 1:
									val = addridx
									
								elif len(addridx.split(",")) == 2:
									(addr,idx) = addridx.split(",")
									val = addr
									args.append(val)
									
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
								
								if comment:
									foobuff = ["# " + comment]
								else:
									foobuff = []
									
									
								if "," not in addridx or addridx[:2] == "''":   #this whole section is a bit of a mess
									lst = [addridx]
								else:
									lst = addridx.split(",")

								for li in lst:
									(dtype,lambdaparser) = detectarg(cur_address,SYMBOLS,li)
									data = parsearg(cur_address,SYMBOLS,li)()  #fixme, i think this breaks symbolic data
									data = pack_data(dtype,data)
									
									if dtype in ["str"]:
										if comment:
											foobuff2 = ["#"+li+" - "+comment]
										else:
											foobuff2 = ["#"+li]

										foobuff = []
									else:
										foobuff2 = []
										
									for d in data:
										program_listing.append((lnum,cur_address,op,indirect_bit,["'%06o" % d]+foobuff2+foobuff, LOADER_FORMATS[DIRECT_LOAD][1] | ( LOADER_BITMASKS["X_FLAG"] * x_flag ), lambda x=d:[x],supress_output))
										cur_address += 1
										foobuff = []
										foobuff2 = []

								handled = True
								continue

							elif op == "EQU":
								if label not in SYMBOLS:
									SYMBOLS[label] = ("int",parsearg(cur_address, SYMBOLS, addridx)()) #first pass only
								else:
									print("****\n%s:%d duplicate symbol definition\n***" % (filename,lnum))
									sys.exit(-1)
								
							elif op == "DAC": #not right fixme
								idx = False
								x_flag = False
								
								if len(addridx.split(",")) == 1:
									val = addridx
									args.append(val)
									
								elif len(addridx.split(",")) == 2:    #fixme
									(addr,idx) = addridx.split(",")
									val = addr
									args.append(val)
									if int(idx):
										x_flag = True
										args.append("1")
										
								if comment:
									args.append("#%s"%comment)
								
#								idx = True
#								print("mooo",LOADER_BITMASKS["I_FLAG"] * idx)
								program_listing.append((lnum,cur_address,"DAC",indirect_bit, args, LOADER_FORMATS[MREF_LOAD][1] | ( LOADER_BITMASKS["R_FLAG"] * r_flag )|( LOADER_BITMASKS["X_FLAG"] * x_flag) |  ( LOADER_BITMASKS["I_FLAG"] * i_flag )|(0o13 << 17) ,lambda x=cur_address,y=val:[parsearg(x,SYMBOLS,y)()],supress_output))
								handled = True
								cur_address += 1
								continue
								
							elif op == "EAC": #not right either
								daceac_bit = True
								idx  = False
								x_flag= true
								if len(addridx.split(",")) == 1:
									val = addridx
									args.append(val)
									 
								elif len(addridx.split(",")) == 2: #fixme too
									(addr,idx) = addridx.split(",")
									val = addr
									args.append( val)
									if int(idx):
										idx = True
										args.append("1")
										
								if comment:
									args.append("#%s"%comment)
								program_listing.append((lnum,cur_address,"EAC",args, LOADER_FORMATS[MREF_LOAD][1] | ( LOADER_BITMASKS["R_FLAG"] * r_flag )|( LOADER_BITMASKS["X_FLAG"] * x_flag ) |( LOADER_BITMASKS["I_FLAG"] * i_flag )|(0o17 << 17) ,lambda x=cur_address,y=val:[parsearg(x,SYMBOLS,y)()]),supress_output)
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
								args.append(unit)

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
	

def asm_pass_2(object_code):
	
	idx = 0
	absfile = {}
	current_addr = 0
	org_addr = 0
	absfile[org_addr] = []
	while idx < len(object_code):
		v,ol = object_code[idx]
		fmt = (0xc00000 & v) >> 22
		val = v & 0x3fffff
		handled = False
		
		if fmt == 0b00:
			zeros = (val & 0x3f0000) >> 17
			val = v & 0xffff
			
			print("%06o\t" % val, ol)
			absfile[org_addr].append((val,ol))
			handled = True
			idx += 1
			current_addr+=1

		elif fmt == 0b01:
			r =   (val & 0x200000) >> 21
			x = (val & 0x10000) >> 16
			i = (val & 0x8000) >> 15
			addr = (val & 0x7fff)
			opcode = (val & 0x1e0000) >> 17
			map = True #i dont know why it is but it is
			#map bit! #reloc bit #DAC #EAC FIXME
			if opcode == 0o13:
				addr = (val & 0x3fff) | (x * 0x8000)  | (i * 0x4000)#14 bit
				print("%06o\t" % addr, ol)
				absfile[org_addr].append((addr, ol))
				
			elif opcode == 0o17: #im not sure this is right, if i did the indirect bit right in 0o13
				addr = (val & 0x7fff) | (x * 0x8000)  | (i * 0x4000) #15 bit
				print("%06o\t" % addr, ol)
				absfile[org_addr].append((addr, ol))
				
			else:
				print("%06o\t" % ((opcode << 12) | (x << 11) | (i << 10) |  (map << 9) |((addr + org_addr)  & 0x7fff)), ol)
				absfile[org_addr].append(((opcode << 12) | (x << 11) | (i << 10) | (map << 9)| ((addr + org_addr) & 0x7fff),ol) )
			handled = True
			idx += 1
			current_addr+=1

		elif fmt == 0b10:
			idx += 1
			current_addr+=1
			cd = (0xc00000 & full_tape[idx]) >> 22
			if cd == 0x00:
				print("sub def")
			elif cd == 0x01:
				print("sub call")
			elif cd == 0x02:
				print("common def")
			elif cd == 0x03:
				print("common req")
				

		elif fmt == 0b11:
			r =   (val & 0x200000) >> 21
			opcode = (val & 0x1e0000) >> 17
			isliteral = val &0x10000
			
			if(isliteral):
				literal = (val & 0xffff)
				if opcode == 0: #augmented opcodes
					augmentcode = (val & 0x3f)
					
			else: #special action
				address = (val & 0x7fff)
				n = (val & 0x8000) >> 15
#				print("****",opcode)
				if opcode==0:
#					print("set org")
					current_addr = address
					absfile[org_addr] = []

				elif opcode == 1:
#					print("end")
					return absfile
		
				handled = True
			idx += 1
			current_addr+=1

		if not handled:
			
			print("------\t",ol)
			
			absfile[org_addr].append((0,ol))
			
	return absfile

def load_file(filename):
	f = open(filename)
	ll = f.readlines()
	f.close()
	return ll

def write_symbols(filename):
	fn = "%s.sym"  % filename
	print("writing symbols %s" % fn)
	f = open(fn, "w")
	f.write(json.dumps(SYMBOLS))
	f.close()


filename = sys.argv[1]
(addr_mode,program_listing) = asm_pass_1(filename)

write_symbols(".".join(filename.split(".")[:-1]))


print("creating relocatable binary")
relocatable_file = []
for (lnum,cur_address,op,indirect_bit,args,oparg,oparg_calc,supress) in program_listing:
	if oparg != None:
		for v in oparg_calc():
			label = ""
			
			for s,a in SYMBOLS.items():
				if a[1] == cur_address:
					label = s

			if indirect_bit:
				indir = "*"
			else:
				indir = " "
#			if v < 0:
#				val = l[3] | (abs(v) | 0x8000) #its a 16 bit value so to fix the sign bit
#			else:
#				indir = " "
				
			if not label:
				label = "    "
			else:
				label = label.ljust(4," ")
				
				
			if isinstance(v,list):
				for vv in v:
					val = oparg | vv
		
					if len(args) and args[-1][0] == "#":
						testbuff = "%s %s%s %s" % (label,op, indir, ",".join(args[:-1]))
						buf = " *"+args[-1][1:]
						testbuff += buf.rjust(27 + (len(buf) - len(testbuff))," ")
					else:
						testbuff = "%s %s%s %s" % (label,op, indir, ",".join(args))
					outline  = "%04x\t%08o\t%s\t\t\t" % (cur_address,val,testbuff)
					relocatable_file.append((val,outline))
					
			else:
				val = oparg | v
				 
				if len(args) and args[-1][0] == "#":
					testbuff = "%s %s%s %s" % (label,op, indir, ",".join(args[:-1]))
					buf = " *"+args[-1][1:]
					testbuff += buf.rjust(27 + (len(buf) - len(testbuff))," ")
				else:
					testbuff = "%s %s%s %s" % (label,op, indir, ",".join(args))

				outline  = "%04x\t%08o\t%s\t\t\t" % (cur_address,val,testbuff)
				relocatable_file.append((val,outline))
				
			if not supress:
				print(outline)

	else:
		relocatable_file.append((0x0,"ERROR!"))
		print(l)




if addr_mode == MODE_RELATIVE:
	print("writing object binary")
	fn = "%s.obj"  % ".".join(filename.split(".")[:-1])
	f = open(fn, "wb")
	for val,line in relocatable_file:
		f.write(struct.pack("3B", (val & 0xff0000) >> 16, (val & 0xff00) >> 8,(val & 0xff) ))
	f.close()
	
else:
	print("lol i dont really know what im doing")
	
	print("running second pass on object output")
	absolute_file = asm_pass_2(relocatable_file)
	
	
	for ml,absf in absolute_file.items():
		fn = "%s-ORG_%04x.bin"  % (".".join(filename.split(".")[:-1]), ml)
		print("writing absolute binary %s" % fn)
		f = open(fn, "wb")
		
		for val,line in absf:
			f.write(struct.pack(">H", val))
			
	f.close()

	print("uh.. we dont really support absolute mode right now")
