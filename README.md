# sel810asm
it can almost assemble its own bootloader!

<pre>
(base) lil-Euclid-10:sel810asm phar$ python asm.py
writing text
load offset: 0x0200 [0o001000]
	Line#: 0007	 Addr: 512	OCT: 130102	HEX: 0xb042
	Line#: 0008	 Addr: 513	OCT: 001000	HEX: 0x0200
	Line#: 0009	 Addr: 514	OCT: 170302	HEX: 0xf0c2
	Line#: 0010	 Addr: 515	OCT: 000022	HEX: 0x0012
	Line#: 0011	 Addr: 516	OCT: 111006	HEX: 0x9206
	Line#: 0012	 Addr: 517	OCT: 111002	HEX: 0x9202
	Line#: 0013	 Addr: 518	OCT: 170302	HEX: 0xf0c2
	Line#: 0014	 Addr: 519	OCT: 001016	HEX: 0x020e
	Line#: 0015	 Addr: 520	OCT: 174302	HEX: 0xf8c2
	Line#: 0016	 Addr: 521	OCT: 033016	HEX: 0x360e
	Line#: 0017	 Addr: 522	OCT: 000022	HEX: 0x0012
	Line#: 0018	 Addr: 523	OCT: 000026	HEX: 0x0016
	Line#: 0019	 Addr: 524	OCT: 113017	HEX: 0x960f
	Line#: 0020	 Addr: 525	OCT: 111006	HEX: 0x9206
	Line#: 0021	 Addr: 526	OCT: 007671	HEX: 0x0fb9
	Line#: 0022	 Addr: 527	OCT: 007673	HEX: 0x0fbb
writing binary
writing symbols boot.sym

TODO:
	strings are probably not handled correctly
	defintly not using the map bit right
	DAC/EAC pseudo instructions do not work right at all
	i still dont know what how the ** operator is supposed to work
	i need to be able to import library symbols but i dont know them
	FORM,FDAT,BSS,BES,CALL, MOR,NAME,ZZZ,END,LIST,NOLS pseudo opcodes
	macros are not supported	

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
</pre>
