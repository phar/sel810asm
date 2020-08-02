************************************************
* TEST EXTERNAL UNIT, TEU.CH '40 BITS 0-3      *
*                                              *
* LOCATION '6000                               *
* PRESS SETPOINT EXECUTE SW AND PROGRAM        *
* WILL PRINT$ UNTIL RELEASED.                  *
* PRESS RECALL SW AND PROGRAM WILL PRINT R     *
* UNTIL RELEASED..                             *
* PRESS WARN SW (HI TEMP) BESIDE WATCHDOG      *
* RELAY AND PROGRAM WILL PRINT W.              *
* PRESS OFF SW CHI TEMP SHUTDOWN> BESIDE WATCH *
* DOG RELAY AND PROGRAM WILL PRINT.            *
*                                              *
* LOCATION '6200                               *
* CHECK SWITCH CONT.ACTS AND ASSOC. LOGIC      *
* FOR NIXIE SWITCHES SS,6,7 AND SB.            *
* PROGRAM WILL DISPLAY SW POSITION OF SS,6     *
* AND S7 IN-ASSOC. NIXIE ONCE EACH SECOND.     *
* TO DISPLAY ONE SWITCH ONLY, SET SENSE SW     *
* CORRESPONDING TO NIXIE SWITCH NO.            *
* TO DISPLAY SETPOINT SW SB, SET SENSE SW NO 8,*
* THE UNITS TENS AND HNDS WILL APPEAR IN RIGHT *
* NIXIE AND THOUS DIGIT WILL APPEAR IN CENTER  *
* NIXIE                                        *
*                                              *
* LOCATION '6400                               *
* CHECK NIXIE TUBES                            *
* PROGRAM WILL DISPLAY SECONDS FROM CLOCK IN   *
* NIXIES AT-ONE SECOND INTERVALS.              *
*                                              *
* LOCATION '6430                               *
* INHIBIT ALARM TRANSMISSION TO CHICAGO        *
* * PROG WILL TST FOR FUNCT 72 AND VALID TIME* *
* <MAX 120) IN SW8. IF BOTH VALID IT WILL      *
* TURN ON ALARM INHIBIT LIGHT AND DISPLAY      *
* DELAY TIME IN NIX WITH FUNCT 72. TIME IS     *
* TESTED IN SEC RATHER THAN MINUTES.           *
*                                              *
     REL
     SPB  CRLF                      PRINT 60 CHAR PER LINE
     LAA  ='177717
     STA  CNTR
STRT NOP
     TEU  '40                       SET POINT EXEC
     DATA '100000
     BRU  SETP
     TEU  '40
     DATA '40000                    HI TEMP SHUT DOWN
     BRU  OFF
     TEU  '40
     DATA '20000                    HI TEMP WARNING
     BRU  *+2
     BRU  WARN
     TEU  '40
     DATA '10000                    ALARM RECALL
     BRU  RECL
     BRU  STRT
SETP LAA  ='151400                  PRINT S
     SPB  AOP
     MOP  '43,W
     DATA '100000                   RESET ST PT EXEC
     BRU  STRT
OFF  LAA  ='147400                  PRINT 0
     SPB  AOP
     BRU  STRT
WARN LAA  ='153400                  PRINT W
     SPB  AOP
     BRU  STRT
RECL LAA  ='151000                  PRINT R
     SPB  AOP
     MOP  '43,W
     DATA '4000                     RESET ALARM RECALL
     BRU  STRT
AOP  HLT
     IMS  CNTA                      COUNTER F/DLY
     BRU  *+1                       CHANGE TO BRU -1 F/DLY
     AOP  1, W
     IMS  CNTR
     BRU* AOP
     LAA  ='177717
     STA  CNTR
     SPB  CRLF
     BRU* AOP
CRLF HLT
     MOP  1,W
     DATA '106400
     MOP  1,W
     DATA '105000
     BRU* CRLF
CNTR DATA 0
CNTA DATA 0
     **** ********                  **********************
     ORG  '200
     AIP  '40,W                     INPT SEC
     STA  CMPR                      STORE F/COMPARE
BEGN AIP  '40,W                     INPT SEC
     CMA  CMPR
     BRU  *+2
     BRU  BEGN
     STA  CMPR
     SNS  8                         SETPOINT SW S8
     BRU  STPT
     SNS  5                         LEFT SW S5
     BRU  LEFT
     SNS  6                         CNTR SW S6
     BRU  CNIX
     SNS  7                         RIGHT SW S7
     BRU  RITE
     AIP  '43,W                     INPT S5 LEFT SW
     LSL  4
     RSL  4
     AOP  '40,W                     DSPLA S5 IN L NIX
     AIP  '44,W                     INPT S6 CNTR SW
     RSL  8
     AOP  '41, W                    DSPLA S6 INC NIX
     AIP  '44,W                     INPT S7 RIGHT SW
     LSL  8
     RSL  8
     AOP  '42, W                    DISPLA S7 IN R NIX
     BRU  BEGN
STPT CLA
     AOP  '40,W                     CLR LEFT NIX
     AIP  '45,W                     INPT S8 SETPT SW
     AOP  '42,W                     DSPLA UTH S8 IN R NIX
     RSL  12
     AOP  '41,W                     DSPLA THOU OF S8 IN C NIX
     BRU  BEGN
LEFT CLA
     AOP  '41,W                     CLR C NIX
     AOP  '42,W                     CLR R NIX
     AIP  '43,W                     INPT 55
     LSL  4
     RSL  4
     AOP  '40,W                     OUPT TO L NIX
     BRU  BEGN
CNIX CLA
     AOP  '40,W                     CLR L NIX
     AOP  '42,W                     CLR R NIX
     AIP  '44,W                     INPT S6
     RSL  8
     AOP  '41,W                     OUPT TO C NIX
     BRU  BEGN
RITE CLA
     AOP  '40,W                     CLR L NIX
     AOP  '41,W                     CLR C NIX
     AIP  '44,W                     INPT S7
     LSL  8
     RSL  8
     AOP  '42,W                     OUPT TOR NIX
     BRU  BEGN
CMPR DATA 0
     **** ********                  ***********************
     ORG  '400
     AIP  '40,W                     INPUT SEC
     LSL  12                        SAVE UNITS ONLY
     STA  DATA                      STA F/COMPARE
BIGN AIP  '40,W
     LSL  12
     CMA  DATA                      CK F/1 SEC CHNG
     BRU  *+2
     BRU  BIGN                      WAIT F/NXT SEC
     STA  DATA
     RSL  4
     STA  TEMP
     RSL  4
     AMA  TEMP
     RSL  4
     AMA  TEMP
     AOP  '40,W
     AOP  '41,W
     AOP  '42,W
     BRU  BIGN
TEMP DATA 0
DATA DATA 0
     **** ********                  ***********************
     ORG  '430
     CLA
     STA  LOCA
     BRU  RSET
HOME IMS  LOCC
     BRU  *-1
     TEU  '40
     DATA '100000                   SET PT EXEC
     BRU  *+2
     BRU  HOME+2
     AIP '44,W                      SW 7
     LSL  8                         SHIFT SW6 OFF
     CMA  ='71000                   SW7=FUNCT 72
     BRU  *+2
     BRU  *+9
     SPB  FNCT                      WRONG FNCT NO
RSET LAA  ='100000
     AOP  '43,W                     RESET SET PT
     CLA
     AOP  '40,W
     AOP  '41,W                     CLR NIX
     AOP  '42,W                     CLR NIX
     BRU  HOME
     AIP  '45,W                     SW8 F/INHIBIT TIME
     STA  LOCB
     SAS                            ADD F/INQUISITIVE TECHN
     BRU  EROR
     BRU  *+1
     BRU  *+1
     CMA  ='440                     TIME MORE THAN 120
     BRU  *+1
     BRU  *+3                       ='440 OR 120
EROR SPB  SORY
     BRU  RSET
     LAA  ='101000
     AOP  '43,W                     RSET ST PT-TRN ON LIGHT
     LAA  LOCB
     BRU  *+3
AGAN LAA  LOCB
     SMA  =1                        SUBT 1 F/CNT
     STA  LOCB
     SAZ
     BRU  *+2
     BRU  OFFF                      TRN OFF LIGHT
     LSL  8
     CMA  ='177400                  CK F/INVALID BCD
     BRU  *+2
     BRU  SUBX                      SUBT '146
     LSL  4
     CMA  ='170000                  CK F/INVALID BCD
     BRU  *+2
     BRU  SUB6                      SUBT 6
AOPP NOP
     AIP  '43,W                     LFT NIX
     LSL  8
     SMA  ='071000
     SAZ
     BRU  *+2
     BRU  A40
     CLA
     AOP  '40,W                     CLR NIX
     BRU  *+3
A40  LAA  LOCB
     AOP  '40,W
     AIP  '44,W                     CNTR NIX
     RSL  8
     SMA  ='162
     SAZ
     BRU  *+2
     BRU  A41
     CLA
     AOP  '41,W                     CLR NIX
     BRU  *+3
A41  LAA  LOCB
     AOP  '41,W
     AIP  '44,W                     RT NIX
     LSL  8
     SMA  ='071000
     SAZ
     BRU  *+2
     BRU  A42
     CLA
     AOP  '42,W                     CLR NIX
     BRU  *+3
A42  LAA  LOCB
     AOP  '42,W
     LAA  LOCA
     SAZ
     BRU  TIME
     AIP  '40,W                     INPT SEC
     STA  LOCD
     IMS  LOCA
TIME TEU  '40
     DATA '100000
     BRU  HOME+6
     AIP  '40,W
     CMA  LOCD
     BRU  *+2
     BRU  TIME
     STA  LOCD
     BRU  AGAN
SUBX LAA  LOCB                      SUBT '146
     SMA  ='146
     STA  LOCB
     BRU  AOPP
SUB6 LAA  LOCB                      SUBT 6
     SMA  ='6
     STA  LOCB
     BRU  AOPP
OFFF CLA                            TRN OFF LITE, CLR NIX
     AOP  '40,W
     AOP  '41,W
     AOP  '42,W
     AOP  '43,W
     SPB  RESM
     BRU  RSET
SORY HLT                            CNT IN SW 8 OVER 120
     SPB  CRLF
     LBA  =-18
     LAA  TBLA+18,1
     SPB  TTY
     IBS
     BRU  *-3
     BRU* SORY
FNCT HLT                            SW 7 NOT 72
     SPB  CRLF
     LBA  =-17
     LAA  TBLB+17,1
     SPB  TTY
     IBS
     BRU  *-3
     BRU* FNCT
RESM HLT
     SPB  CRLF
     LBA  =-19
     LAA  TBLC+19,1
     SPB  TTY
     IBS
     BRU  *-3
     BRU* RESM
TTY  HLT
     AOP  1,W
     LSL  8
     AOP  1,W
     BRU* TTY
LOCA DATA 0
LOCB DATA 0
LOCC DATA 0
LOCD DATA 0
TBLA DATA ''REDUCE CNT IN SW8 TO 120,EXEC SET-PT''
TBLB DATA ''SELECT FUNCT 72, EXECUTE SET POINT''
TBLC DATA ''ALARMS WILL BE TRANSMITTED TO CHICAG''
     END
