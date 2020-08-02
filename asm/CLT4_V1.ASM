*************************************************
* 1/0 CONTROLLER DIAGNOSTIC
*
* 1= AOP 44, AIP 46                     P1-P5
* 2= AOP 45, AIP 47                     P1-P5
* 3= AOP 46, AIP 50 BITS 8-15           P1-P5
* 4= AOP 46, AIP 50 BITS 0-7            P2-P6
* 5= AOP 44, AIP 51                     P2-P5
* 6= AOP 47, AIP 51                     P2-P6
* 7= AOP 50, AIP 52                     P2-P6
* 8= AOP 51, AIP 53                     P3-P7
* C=CLEAR LCS MODE
* G=INHIBIT HALT ON ERROR
* H=HALT PROGRAM ON EROR • 'A' '=OK ' '8' '=ERO R
* L=LCS..1 TEST BIT WITH CONTROL PANEL SWITCH
* P=PRINT TEST RESULTS
* PREPARED BY CARL L THOMPSON 4-15-76
********************************************'****
     REL
     DATA '10001
     CEU  1,W
     DATA '62000
     LAA  TTY1
     STA* IO16
     LAA  ='40000                    TRN SYS ON
     AOP  '43,W
     SPB  CLIR
     LAA  ZERO
     SAZ
     BRU  BEGN
     SPB  CRLF
     SPB  CRLF
     LBA  =-22                      NXT 18 PRNT PRELIMINARY
     LAA  TBLH+22,1                 INSTRUCTIONS
     SPB  TTY0
     IBS
     BRU  *-3
     SPB  CRLF
     LBA  =-25
     LAA  TBLH+47,1
     SPB  TTY0
     IBS
     BRU  *-3
     SPB  CRLF
     LBA  =-29
     LAA  TBLH+76,1
     SPB  TTY0
     IBS
     BRU  *-3
     SPB  CRLF
     LAA  =1                        TYPE INSTR 1 TIME ONLY
     STA  ZERO
BEGN NOP
     NOP
     BRU  *-1
     NOP
STRT NOP
     CEU  1
     DATA '62000
     NOP
     LAA  ='40000
     AOP  '43,W
LBA  LBA  =-16                      OR LBA=-8
     LAA  =1
     AMA  TBLA                      NO OF TESTS
     STA  TBLA
LAA  LAA  BITS+16,1
AGAN NOP                            OR LCS
     STA  CHEK
AOP  AOP  '44,W
     NOP
     IMS  NEG1
     BRU  *-1
     NOP
AIP  AIP  '46,W
     STA  TEMP
     NOP                            OR BRU LOGS F/LGS
     LAA  CHEK
     CMA  TEMP
     BRU  *+2
     BRU  *+2
     BRU  EROR
     LAA  =1
AMA  AMA  TBLB+16,1
STA  STA  TBLB+16,1               STORE GOOD TSTS
     BRU  DLY
EROR STB  CNTO
     LBA  TEMP                      EROR
HALT NOP                            OR HALT F/H
     LBA  CNTO
     NOP
     NOP
DLY  NOP
     NOP
     IBS
     BRU  LAA
     BRU  STRT                      RE-STRT TST
LOCS NOP                            USED F/LCS ONLY
     LAA  ='40000
     AOP  '43,W
     LBA  TEMP
     LAA  CHEK
     CMA  TEMP
     BRU  *+2
     BRU  *+4
     NOP
HOLT NOP                            OR HALT F/H
     NOP
     IMS  NTH0
     BRU  *-1
     BRU  LAA
TTYR DAC  **
     SPB  CRLF
     AIP  1,W
     STA  CNTA
     LSL  8
     AOP  1,W
     SPB  CRLF
     LAA  CNTA
     CMA  ='314                     L=LCS
     BRU  *+2
     BRU  LCSS
     CMA  ='303                     C=CLEAR LCS MODE
     BRU  *+2
     BRU  CLER
     CMA  ='320                     P=PRINT TSTS
     BRU  *+2
     BRU  PRNT
     CMA  ='307                     G=GO
     BRU  *+2
     BRU  GO
     CMA  ='310                     H=HALT
     BRU  *+2
     BRU  STOP
     CMA  ='261                     =1 AOP 44., AIP 46
     BRU  *+2
     BRU  ONE
     CMA  ='262                     =2 AOP 45., AIP 47
     BRU  *+2
     BRU  TOO
     CMA  ='263                     =3 AOP 46., AIP 50 0-7
     BRU  *+2
     BRU  THRE
     CMA  ='264                     =4 AOP 46., AIP 50 8-15
     BRU  *+2
     BRU  FOUR
     CMA  ='265                     =5 AOP 44., AIP 51
     BRU  *+2
     BRU  FIVE
     CMA  ='266                     =6 AOP 47, AIP 51
     BRU  *+2
     BRU  SIX
     CMA  ='267                     =7 AOP XX., AIP 52 #MIKE FIXME
     BRU  *+2
     BRU  SEVN
     CMA  ='270                     =8 AOP 51., AIP 53
     BRU  *+2
     BRU  EGHT
     BRU  INVL                      INVALID REQUEST
PRNT LAA  CNTS                      DAG PRIT
     STA  TTYR
     BRU  TOI+3
LCSS LAA  LCS
     STA  AGAN
     LAA  BRU
     STA  AIP+2
     BRU  TOI
CLER LAA  NOP
     STA  AIP+2
     STA  AGAN
     BRU  TOI
GO   LAA  NOP
     STA  HALT
     STA  HOLT
     BRU  TOI
STOP CLA
     STA  HOLT
     STA  HALT
     BRU  TOI
ONE  LAA  CNT1                      AOP 44
     STA  AOP
     LAA  CNTJ                      AIP '46,XX  #MIKE FIXME
     STA  AIP
     LAA  OU4                       OUT CH 44
     STA  TBLE+14
     LAA  IN6                       IN CH 46
     STA  TBLE+7
     BRU  ALL                       TST 16 BITS
TOO  LAA  CNTB                      AOP 45
     STA  AOP
     LAA  CNTC                      AIP '47., W
     STA  AIP
     LAA  OU5                       OUT CH 45
     STA  TBLE+14
     LAA  IN7                       IN CH 47
     STA  TBLE+7
     BRU  ALL                       TST 1 6 BITS
THRE LAA  CNTD                      AOP 46 8-15
     STA  AOP
     LAA  CNTE                      AIP 50 8-15
     STA  AIP
     LAA  CNT2                      8- F/BIT
     STA  TBLD+15                   TST IN CH OUT CH BIT 0-0
     LAA  CNT3                      15  F/BIT
     STA  TBLD+16
     LAA  CNTP                      LAA BITS+X6.,1  #MIKE FIXME
     STA  LAA
     BRU  PART
FOUR LAA  CNT4                      AOP 46 0-7
     STA  AOP
     LAA  CNT5                      AIP 50 0-7
     STA  AIP
     LAA  CNT6                      0-F /BIT
     STA  TBLD+15                   TST IN CH OUT CH BIT 0-0
     LAA  CNT7                      7 SPC F/BI T
     STA  TBLD+16
     LAA  CNT8                      LAA BITS+8.,1
     STA  LAA
     LAA  CNTG                      AMA TBLB +8, 1
     STA  AMA
     LAA  CNTH                      STA TBLB+8.,1
     STA  STA
     BRU  PART
FIVE LAA  CNTU                      AOP 44
     STA  AOP
     LAA  CNTV                      AIP 51
     STA  AIP
     LAA  OU4                       OUT CH 44
     STA  TBLE+14
     LAA  IN1                       IN CH 51
     STA  TBLE+7
     BRU  ALL                       TST 16 BITS
SIX  LAA  CNTW                      AOP 47
     STA  AOP
     LAA  CNTV                      AIP 51
     STA  AIP
     LAA  OU7                       OUT CH 43
     STA  TBLE+14
     LAA  IN1                      IN CH 51
     STA  TBLE+7
     BRU  ALL                       TST 1 6 BITS
SEVN LAA  CNTX                      AOP 50
     STA  AOP
     LAA  CNTY                      AIP 52
     STA  AIP
     LAA  OU8                       OUT CH 50
     STA  TBLE+14
     LAA  IN2                       IN CH 52
     STA  TBLE+7
     BRU  ALL                       TST 16 BITS
EGHT LAA  CNT2                      AOP 51
     STA  AOP
     LAA  CNT1                      AIP 53
     STA  AIP
     LAA  OU9                       OUT CH 51
     STA  TBLE+14
     LAA  IN3                       IN CH 53
     STA  TBLE+7
     BRU  ALL                       TST 1 6 BITS
PART NOP
     LAA  CNTF                      LBA=-8
     STA  LBA                       LBA=-8
     LBA  =-17
     LAA  TBLD+17,1
     SPB  TTY0
     IBS
     BRU  *-3
     BRU  TOI
ALL  NOP
     LAA  CNTL                      STA TBL8+16,1
     STA  STA
     LAA  CNTK                      AMA TBLB+ 16, 1
     STA  AMA
     LAA  CNTN                      LBA=-16
     STA  LBA
     LAA  CNTP                      LAA BITS+X6,1 #MIKE FIXME
     STA  LAA
     LBA  =-15
     LAA  TBLE+15,1                 TST IN CH XX OUT CH XX
     SPB  TTY0
     IBS
     BRU  *-3
     BRU  TOI
INVL SPB  CRLF
     LBA  =-8
     LAA  TBLC+8,1                  INVALID REQ
     SPB  TTY0                      7
     IBS
     BRU  *-3
     BRU  TOI+3
TOI  SPB  CLIR
     LAA  CNTM                      BRU TO STRT
     STA  TTYR
     SPB  CRLF
     TOI
     BRU* TTYR
TTY0                               #MIKE FIXME TTY0 OR TTYO
     AOP  1,W
     LSL  8
     AOP  1,W
     BRU* TTY0
CRLF HLT
     MOP  1,W
     DATA '106400
     MOP  1,W
     DATA '105000
     BRU* CRLF
TSTS HLT                            CONV OCTAL TO DEC
     STB  TEMP
     TAB
     LAA  =-5
     STA  CNTO
     CLA
     BRU  *+3
CLA  CLA
     MPY  =10
     DIV  =10000
     AMA  ='260
     LSL  8
     AOP  1,W
     IMS  CNTO
     BRU  CLA
     LBA  TEMP
     BRU* TSTS
BINO HLT                            ARRANGE AND OPT BIT NO
     STB  TEMP
     TAB
     CLA
     LAA  CNTQ                      F/PRNT 0-9 BITS
     SAZ
     BRU  *+2
     BRU  TWO                       F/PRINT 10-15 BITS
     CLA
     FLL  13
     AMA  ='260
     LSL  8
     AOP  1,W
     MOP  1,W
     DATA '120000
     IMS  CNTQ
     NOP
     LBA  TEMP
     BRU* BINO
TWO  FLL  13                        PRNT BITS 10-15
     AMA  ='260
     LSL  8
     AOP  1,W
     FLL  3
     AMA  ='260
     LSL  8
     AOP  1,W
     LBA  TEMP
     BRU* BINO
PRIT NOP
     LBA  =-7
     LAA  TBLF+7,1                  PRNT HEADING OF TBLF
     SPB  TTY0
     IBS
     BRU  *-3
     LAA  TBLA                      TOTAL TSTS
     SPB  TSTS
     SPB  CRLF
     SPB  CRLF
     LBA  =-8
     LAA  TBLG+8,1                  BIT GOOD TST
     SPB  TTY0
     IBS
     BRU  *-3
     SPB  CRLF
     LAA  =-10
     STA  CNTQ                      =-10 F/B-ITS 0-9
     LAA  =-16
     STA  CNTR
MORE LAA  TBLI,1                    CHAN NO
     SPB  BINO
     SPB  SPCS
     LAA  TBLB,1                    GOOD TSTS
     SPB  TSTS
     SPB  CRLF
     IBS
     NOP
     IMS  CNTR
     BRU  MORE
     SPB  CLIR
     BRU  STRT
CLIR HLT
     LBA  =-17
     CLA
     STA  TBLA+17,1                 CLR TST TBLE
     IBS
     BRU  *-2
     BRU* CLIR
SPCS HLT                            5 SPACES
     LAA  =-5
     STA  CNTT
     LAA  ='120000
     AOP  1,W
     IMS  CNTT
     BRU  *-3
     BRU* SPCS
TTY1 DAC  TTYR
CNTA DATA 0
CNTB DATA '170145
CNTC DATA '170347
CNTD DATA '170146
CNTE DATA '170350                   AIP CH 50
CNTF LBA  =-8
CNTG AMA  TBLB+8,1
CNTH STA  TBLB+8,1
CNT1 DATA '170144
CNTJ DATA '170346
CNTK AMA  TBLB+16,1
CNTL STA  TBLB+16,1
CNTM DAC  STRT
CNTN LBA  =-16
CNTO DATA 0
NOP  NOP
IO16 DATA '1016
HLT  HLT
TBLA DATA 0                         NO OF TSTS
TBLB BSS  20                        STORE GOOD TSTS
BITS DATA '100000,'40000,'20000,'10000,'4000
     DATA '2000,'1000,'400,'200,'100,'40,'20,'10
     DATA 4,2,1
TBLC DATA ''INVALID REQUEST''
TBLD DATA '' TEST IN CH 50 OUT CH 46 BITS 0-7''
TBLE DATA ''TEST INPUT CH 46., OUTPUT CRI 44 ''
TBLF DATA ''TOTAL TESTS = ''
TBLG DATA ''BIT GOOD TESTS''
TBLI DATA 0,'10,'20,'30,'40,'50,'60,'70,'100
     DATA '110,'10,'11,'12,'13,'14,'15
TBLH DATA ''TURN OFF SWITCH S1 NEXT TO WATCH''
     DATA ''DOG RELAY. ''
     DATA ''UNPLUG DISPLAY RELAY CARDS ABOVE''
     DATA '' WATCH DOG RELAY. ''
     DATA ''PRESS THE NUMBER ON TTY ASSIGNED''
     DATA '' TO THE CHANNEL FOR TEST. ''
ZERO DATA 0
NTH0 DATA 0                         DLY CNTR
TEMP DATA 0                         TEMP STORAGE
NEG1 DATA 0
LCS  LCS
BRU  BRU  LOCS
CNTP LAA  BITS+16,1
CNTQ DATA 0                         PRNT
CNTR DATA 0
CNTS DAC  PRIT
CNTT DATA 0
CNTU AOP  '44,W
CNTV AIP  '51,W
CNTW AOP  '47,W
CNTX AOP  '50,W
CNTY AIP  '52,W
CNTZ AOP  '51,W
CNT1 AIP  '53,W
OU4  DATA '132264                   CH 44
OU5  DATA ''45''                    CH 45
OU6  DATA ''46''                    CH 46
OU7  DATA ''47''                    CH 47
OU8  DATA ''50''                    CH 50
OU9  DATA ''51''                    CH 51
IN1  DATA '132661                   CH 51
IN2  DATA ''52''                    CH 52
IN3  DATA ''53''                    CH 53
IN6  DATA ''46''                    CH 46
IN7  DATA ''47''                    CH 47
CNT2 DATA '134255                   8-
CNT3 DATA '130665                   1 5 F/BIT
CNT4 AOP  '46,W
CNT5 AIP  '50,W
CNT6 DATA '130255                   O-
CNT7 DATA '133640                   7 SPC F/BIT
CNT8 LAA  BITS+8,1
CHEK DATA 0
     END
