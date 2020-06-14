***************************
* boot strap loader from tape
****************************
     ORG  '001000
*i still dont know what CHAN actually is
CHAN EQU  '007673
UNIT EQU  2
STRT CEU  UNIT,W
     DATA '001000
     AIP  UNIT,W
     SAZ
     BRU  * +2
     BRU  * -3
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


* wait macro
WAIT MACR
@1   NOP
     NOP
     NOP
	 BRU @1
     EMAC
