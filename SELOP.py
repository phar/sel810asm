

PSEUDO_OPCODES = {"ABS":(), "REL":(), "ORG":(),"EQU":(),"DAC":(),"EAC":(),"DATA":(),"END":(), "FORM":(),"FDAT":(),"BSS":(),"BES":(),
			      "CALL":(),"MOR":(),"NAME":(),"ZZZ":(),"END":(),"LIST":(),"NOLS":(),"***":(),"MACR":(),"EMAC":()}

MREF_OPCODES = {"LAA":0o1,"LBA":0o2,"STA":0o3,"STB":0o4,"AMA":0o5,"SMA":0o6,"MPY":0o7,"DIV":0o10,"BRU":0o11,"SPB":0o12,"IMS":0o14,"CMA":0o15,"AMB":0o16}

AUGMENTED_OPCODES = { "ABA":(0,0o27),"ASC":(0,0o20),"CLA":(0,0o3), "CNS":(0,0o34),"CSB":(0,0o7), "FLA":(0,0o17),"FLL":(0,0o13),"FRA":(0,0o12),
					  "FRL":(0,0o14),"HLT":(0,0o0), "IAB":(0,0o6), "IBS":(0,0o26),"ISX":(0,0o51),"LCS":(0,0o31),"LIX":(0,0o45),"LOB":(0,0o36),
					  "LSA":(0,0o11),"LSL":(0,0o16),"NEG":(0,0o2), "NOP":(0,0o33),"OBA":(0,0o30),"OVS":(0,0o37),"RNA":(0,0o1), "RSA":(0,0o10),
					  "RSL":(0,0o15),"SAN":(0,0o23),"SAP":(0,0o24),"SAS":(0,0o21),"SAZ":(0,0o22),"SNO":(0,0o32),"SOF":(0,0o25),"STX":(0,0o44),
					  "STB":(0,0o50),"TAB":(0,0o5), "TAZ":(0,0o52),"TBA":(0,0o4), "TBP":(0,0o40),"TBV":(0,0o42),"TOI":(0,0o35),"TPB":(0,0o41),
					  "TVB":(0,0o43),"TXA":(0,0o53),"XPB":(0,0o47),"XPX":(0,0o46),"SNS":(0o13,0o4)}
					  
IO_OPCODES = {"CEU":(0o13,0o00),"TEU":(0o13,0o01),"MIP":(0o17,0o03),"MOP":(0o17,0o02),"AIP":(0o17,0o01),"AOP":(0o17,0o00)}

INT_OPCODES ={"PID":(0o130601,0),"PIE":(0o130600,0)}

SECOND_WORD_OPS = {"CEU":(0),"TEU":(0),"MOP":(0)}

DIRECT_LOAD = 0
MEMREF_LOAD = 1
SUBCALL_LOAD = 2
LITERAL_LOAD = 3
LOADER_FORMATS = {0:("DIRECT_LOAD",0x000000), 1:("MEMREF_LOAD",0x400000),2:("SUBCALL_LOAD",0x800000),3:("LITERAL_LOAD",0xc00000)}
LOADER_BITMASKS = {"R_FLAG":0x200000,"X_FLAG":0x010000,"I_FLAG":0x008000, "DAC":0x08000, "EAC":0x0a0000}

CEU_TEU_UNITS = {0:("INVALID",None,None),
				1:("ASR-33",["ASR33/35"],None),
				2:("Paper Tape Reader and Punch",["Paper Tape Reader and Punch"],None),
				3:("Card Punch",["Card Reader and Punch"],["Card Reader and Punch"]),
				4:("Card Reader",["Card Reader andPunch"],["Card Reader and Punch"]),
				5:("Line Printer",["Line Printer"],["Line Printer"]),
				6:("TCU 1",None,["Magnetic Tape"]),
				7:("TCU 2",None,["Magnetic Tape"]),
				8:("INVALID",None,None),
				9:("INVALID",None,None),
				10:("TypeWriter",None,None),
				11:("X-Y Plotter",["X-Y Plotter"],None),
				12:("Interval Timer",None,None),
				13:("Movable Head Disc Control Unit",None,["Moveable Head Disc"]),
				14:("CRT",["CRT"],None,),
				15:("Fixed Head Disc",None,["Fixed Head Disc"])}



TEU_SECOND_WORDS = {
None:								{"wordmask": 						(0b0000000000000000,0)},
"Card Reader and Punch":			{"wordmask": 						(0b0000000000000000,0),
									"Skip No Punch Error": 				(0b0000000001000000,0)},

"Moveable Head Disc":				{"wordmask": 						(0b0000000000000000,0),
									"Skip If Seek Complete": 			(0b0000100000000000,0),
									"Skip If No Seek Error": 			(0b0000010000000000,0),
									"Skip on Begining of Disc": 		(0b0000001000000000,0),
									"Skip on Begining of Sector": 		(0b0000000100000000,0),
									"Skip if Pack On Line": 			(0b0000000010000000,0),
									"Skip if No Read Overflow": 		(0b0000000001000000,0),
									"Skip If No Write Overflow": 		(0b0000000000100000,0),
									"Skip if No Checksum Overflow": 	(0b0000000000010000,0),
									"Skip if no File Unsafe": 			(0b0000000000001000,0),
									"Skip if DCU REady": 				(0b0000000000000100,0),
									"Skip if Not Busy": 				(0b0000000000000010,0)},
									
"Fixed Head Disc":					{"wordmask": 						(0b0000000000000000,0),
									"Skip on No Program Error": 		(0b1000000000000000,0),
									"Skip on Disc On Line": 			(0b0100000000000000,0),
									"skip on no disc reD overflow": 	(0b0010000000000000,0),
									"skip on no disc write overflow": 	(0b0001000000000000,0),
									"skip on no checksum error": 		(0b0000100000000000,0),
									"skip on no disc file area prot.":	(0b0000010000000000,0),
									"skip on disc controller not busy":	(0b0000001000000000,0)},
									
"Magnetic Tape":					{"wordmask": 						(0b0000000000000000,0),
									"skip on not busy": 				(0b1000000000000000,0),
									"skip on no end of file": 			(0b0100000000000000,0),
									"skip on no overflow": 				(0b0010000000000000,0),
									"skip on load point": 				(0b0001000000000000,0),
									"skip on end of recored interrupt":	(0b0000100000000000,0),
									"skip on no parity error": 			(0b0000010000000000,0),
									"skip on write ring in": 			(0b0000001000000000,0),
									"skip on no end of tape": 			(0b0000000100000000,0),
									"skiop on rewinding": 				(0b0000000010000000,0),
									"skip on no crc error (9 trk)": 	(0b0000000001000000,0)},
									
"Line Printer":						{"wordmask": 						(0b0000000000000000,0),
									"Skip If Not Busy": 				(0b0000100000000000,0),
									"Skip If No Pariry Error": 			(0b0000001000000000,0),
									"Skip if No Bottom Of Form": 		(0b0000000010000000,0),
									"Skip if Printer Operable": 		(0b0000000001000000,0)},
									
"Interval Timer":					{"wordmask": 						(0b0000000001000000,0),
									"Disable Zero Count Interrupt": 	(0b0000000010000000,0)},

}



CEU_SECOND_WORDS = {
None:								{"wordmask": 						(0b0000000000000000,0)},

"Magnetic tape format 0": 			{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,14),
									"Word Transfer Ready Interrupt": 	(0b0010000000000000,13),
									"End of Record Interrupt": 			(0b0001000000000000,12),
									"Rewind": 							(0b0000010000000000,10),
									"Erase Four Inches of Tape": 		(0b0000001000000000,9),
									"BCD\Binary": 						(0b0000000100000000,8),
									"Density":	 						(0b0000000011000000,6),
									"Tape Transport": 					(0b0000000000111000,3),
									"Current word Address In": 			(0b0000000000000100,2),
									"Characters per word": 				(0b0000000000000011,0)},

"Magnetic tape format 1":  			{"wordmask": 						(0b0000100000000000,0),
									"BTC Initalize":		 			(0b1000000000000000,15),
									"P.I. Connected": 					(0b0100000000000000,14),
									"Word Transfer Ready Interrupt": 	(0b0010000000000000,13),
									"End of Record Interrupt": 			(0b0000100000000000,11),
									"Write Record": 					(0b0000010000000000,10),
									"Write End of File": 				(0b0000001000000000,9),
									"Read Record": 						(0b0000000100000000,8),
									"Advance Record": 					(0b0000000010000000,7),
									"Advance\End of file": 				(0b0000000001000000,6),
									"Backspace Record": 				(0b0000000000100000,5),
									"Backspace End of File": 			(0b0000000000010000,4),
									"Current word Address In": 			(0b0000000000000100,3)},
"ASR33/35": 						{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,14),
									"In": 								(0b0010000000000000,13),
									"Out": 								(0b0001000000000000,12),
									"Reader Mode": 						(0b0000100000000000,11),
									"Key Mode": 						(0b0000010000000000,10),
									"Clear": 							(0b0000001000000000,9),
									"Power On": 						(0b0000000100000000,8),
									"Power Off": 						(0b0000000010000000,7)},
"Paper Tape Reader and Punch": 		{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,14),
									"In": 								(0b0010000000000000,13),
									"Out": 								(0b0001000000000000,12),
									"Punch Power On": 					(0b0000100000000000,11),
									"Punch Power Off":					(0b0000010000000000,10),
									"Reader Enable": 					(0b0000001000000000,9),
									"Reader Disable": 					(0b0000000100000000,8)},
"Card Reader and Punch": 			{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"BTC Initalize": 					(0b1000000000000000,15),
									"In": 								(0b0010000000000000,13),
									"Out": 								(0b0001000000000000,12),
									"Feed Card": 						(0b0000100000000000,11),
									"Read Stack Offset": 				(0b0000001000000000,9),
									"Feed Card Punch": 					(0b0000000100000000,8),
									"Eject Card (punch)": 				(0b0000000010000000,7),
									"Punch Stacker Offset": 			(0b0000000001000000,6),
									"Current Word Address In": 			(0b0000000000001000,3)},
"X-Y Plotter": 						{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"Pocess Complete": 					(0b0010000000000000,0),
									"Pen Down": 						(0b0000100000000000,0),
									"Pen Up": 							(0b0000010000000000,0),
									"Drum Down": 						(0b0000001000000000,0),
									"Drump Up": 						(0b0000000100000000,0),
									"Carriage Left": 					(0b0000000010000000,0),
									"Carriage Right": 					(0b0000000001000000,0),
									"Current Word Address In": 			(0b0000000000001000,0)},
"Line Printer": 					{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"End of Print": 					(0b0010000000000000,0),
									"Buffer Not Busy": 					(0b0001000000000000,0),
									"Advance Paper to Format Tape Chan":(0b0000100000000000,0),
									"Advance 1 Line": 					(0b0000010000000000,0),
									"Top of Form": 						(0b0000001000000000,0),
									"Print": 							(0b0000000100000000,0),
									"Clear Buffer": 					(0b0000000010000000,0),
									"Fill Buffer": 						(0b0000000001000000,0),
									"Current Word Address In": 			(0b0000000000001000,0)},
"Line Printer advance": 			{"wordmask": 						(0b0001000000000000,0), #has two formats
									"P.I. Connected": 					(0b0100000000000000,0),
									"End of Print": 					(0b0010000000000000,0),
									"Buffer Not Busy": 					(0b0001000000000000,0),
									"Advance Paper to Format Tape Chan":(0b0000100000000000,0),
									"Advance 1 Line": 					(0b0000010000000000,0),
									"Top of Form": 						(0b0000001000000000,0),
									"Format": 							(0b0000000111000000,6),
									"Current Word Address In": 			(0b0000000000001000,0)},
"Movable head disc seek": 			{"wordmask": 						(0b0000000000001000,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"Seek Error": 						(0b0010000000000000,0),
									"Seek Complete": 					(0b0001000000000000,0),
									"Number of tracks to be moved": 	(0b0000011111110000,3),
									"Current Word Address In": 			(0b0000000000001000,0)},
"movable head read disc data": 		{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"Seek Error": 						(0b0010000000000000,0),
									"Seek Complete":		 			(0b0001000000000000,0),
									"Sector #": 						(0b0000111100000000,8),
									"Head #": 							(0b0000000011110000,4),
									"Current Word Address In": 			(0b0000000000001000,0)},
"fixed head disk select track": 	{"wordmask": 						(0b0000000000000011,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"Checksum or Program Error": 		(0b0000100000000000,0),
									"Read Overflow or Error": 			(0b0000001000000000,0),
									"Track Number": 					(0b0000000111111111,0),
									"Current Word Address In": 			(0b0000000000001000,0)},
"fixed head disk read": 			{"wordmask": 						(0b0000000000000001,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"Checksum or Program Error": 		(0b0010000000000000,0),
									"Read Overflow or Write Error": 	(0b0001000000000000,0),
									"Read Sequential": 					(0b0000100000000000,0),
									"Starting Sector": 					(0b0000000001111000,3),
									"Current Word Address In": 			(0b0000000000001000,0)},
"fixed head disk write": 			{"wordmask": 						(0b0000000000000010,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"Checksum or Program Error": 		(0b0010000000000000,0),
									"Read Overflow or Write Error": 	(0b0001000000000000,0),
									"Write Sequential": 				(0b0000100000000000,0),
									"Starting Sector": 					(0b0000000001111000,3)},
"CRT": 								{"wordmask": 						(0b0000000000000000,0),
									"P.I. Connected": 					(0b0100000000000000,0),
									"Overflow": 						(0b0010000000000000,0),
									"Stop": 							(0b0001000000000000,0),
									"Display On": 						(0b0000100000000000,0),
									"Display Off": 						(0b0000010000000000,0)}



}

