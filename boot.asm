***************************
* boot strap loader from tape
****************************
     ORG  '001000
STRT CEU  U,W
     DATA '001000
     AIP  2,W
     SAZ
     BRU  * +2
     BRU  * -3
READ AIP  2,W,R
     STA  DAC1
     SAZ
     IBS
     BRU  DAC2
DAC1 DAC  CHAN-1,1
DAC2 DAC  CHAN
