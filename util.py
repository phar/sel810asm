import re

from math import floor, log10

def fexp(f):
    return int(floor(log10(abs(f)))) if f != 0 else 0

def fman(f):
    return f/10**fexp(f)
    

def detectarg(curr_address, symbols, argstring):
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
			lambdaparse = lambda x,y=bnext : [ord(x) | 0x80 for x in x[y:-2]] #patches in ASR33 converion of strings
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
				lambdaparse = lambda x,y =curr_address,s=sign : y * s
		else:
			t = "ip"
			lambdaparse = lambda x,y =curr_address,s=sign : y * s

	elif argstring[bnext:] in symbols:
		t = "label"
		lambdaparse = lambda x,y=bnext,s=sign  : symbols[x[y:]][1] * s
		
	else: #bare number.. still more work  these need to be packed into a ye-olde format as words
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
	
	
def parsearg(curr_address,symbols, argstring):
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
			
				t,f = detectarg(curr_address,symbols, argparts[i])
				if t == 'str':
					return lambda x=f : x(argstring)
				else:
					total = lambda x=total, y = lambda x=f,y=argparts[i]: x(y), z=mth: z(x, y)
	return total
