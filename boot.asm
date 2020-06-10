***************************
* boot strap loader from tape
****************************
     ORG  '001000
*i still dont know what CHAN actually is
CHAN EQU  5
UNIT EQU  2
STRT CEU  UNIT,W
     DATA '001000
     AIP  UNIT,W
     SAZ
     BRU  * 2
     BRU  * -3
READ AIP  UNIT,W,R
     LSL  8
     API  UNIT,W,R
     STA* DAC1
     SAZ
     IBS
     BRU* DAC2
     BRU  READ
DAC1 DAC  CHAN-2,1
DAC2 DAC  CHAN
