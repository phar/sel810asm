***************************
* BOOT STRAP LOADER FROM TAPE
****************************
     ABS
CHAN EQU  '007673
UNIT EQU  1
STRT CEU  UNIT,W
     DATA '004000
     AIP  UNIT,W                      commenty
     SAZ
     BRU  *+2
     BRU  *-3
READ AIP  UNIT,W
     LSL  8
     AIP  UNIT,W,R
     STA* DAC1
     SAZ
     IBS
     BRU* DAC2
     BRU  READ
DAC1 DAC  CHAN-2,1
DAC2 DAC  CHAN
     END
