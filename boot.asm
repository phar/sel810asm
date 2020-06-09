***************************
* boot strap loader from tape
****************************
     ORG  '001000
DAC1 EQU  0
DAC2 EQU  2
CHAN EQU  5
STRT CEU  U,W
     DATA '001000
     AIP  2,W
     SAZ
     BRU  *
     BRU  *
READ AIP  2,W,R
     STA  DAC1
     SAZ
     IBS
     BRU  DAC2
     DAC  CHAN-1,1
     DAC  CHAN
