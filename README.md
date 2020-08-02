<pre>

.227 files are direct reads of 24 bit format from tape
.obj files are raw 24 bit loader object files
.bin are raw 16 bit opcode files

# sel810asm
rewritten assembler for the SEL810 system, compatable with the SEL relocatable 24 bit format..


once you've assembled an object file, it can be converted to tape format with obj2RS227.py

you can extract other object files from tape using the objdump tool 

theres a pretty basic disassembler for 16bit executable code "bin" files.

and if i had time, you can convert 24bit relocatable format into direct executable 16 bit code with obj2bin.py


good stuff:
	almost full compliance with the original 810 assembler so the manual can be used... kinda
	works as a two-pass assembler (thank you lambda), though I currently dont support relocatable 
	format.
	

stuff to know:
	the asm format is quite strict and based on the original punch card limitations
labels can only be 4 characters, must start with a letter, the opcode column is also
*always* 4 bytes wide before its arguments and arguments have a limited lengths and on line
comments are part of the "line" and start at  offset 25 on each line and only the DATA
pseudo opcode can span the two

I dont know what the symbols are for the loader libararies, so, i dont account for them in the assembler at all..

#things i dont support
NAME's (library)
CALL's 
libraries
floats
doubles

#notes
</pre>
