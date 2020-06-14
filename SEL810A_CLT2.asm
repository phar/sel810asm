************************************************                                
* TEST EXTERNAL UNIT, TEU.CH '40 BITS 0-3      *                                
* LOCATION '6000                               	*                                 
* PRESS SETPOINT EXECUTE SW AND PROGRAM     	*                                
* WILL PRINT$ UNTIL RELEASED•               *                                
* PRESS RECALL SW AND PROGRAM WILL PRINT R  *                                
* UNTIL RELEASED..                          *                                
* PRESS WARN SW (HI TEMP) BESIDE WATCH DOG  *                                
* RELAY AND PROGRAM WILL PRINT w.           *                                
* PRESS OFF SW CHI TEMP SHUTDOWN> BESIDE WATCH                                
* DOG RELAY AND PROGRAM WILL PRINT o. *                                
*                                               *                                 
* LOCATION '6200 *                                
* CHECK SWITCH CONT.ACTS AND ASSOC. LOGIC *                                
* FOR NIXIE SWITCHES SS,6,7 AND SB. *                                
* PROGRAM WILL DISPLAY SW POSITION OF SS,6 *                                
* AND S7 IN-ASSOC. NIXIE ONCE EACH SECOND. *                                
* TO DISPLAY ONE SWITCH ONLY, SET SENSE SW *                                
* CORRESPONDING TO NIXIE SWITCH NO. * 
* T0 DISPLAY SETPOINT SW SB, SET SENSE SW NO 8,                                
* THE UNITS TENS AN.D HNDS WILL APPEAR IN RIGHT                                
* NIXIE AND THOUS DIGIT WILL APPEAR IN CENTER*                                
* NIXIE• *                                
* *                                 
* LOCATION '6400 * * CHECK NIXIE TUBES *                                
* PROGRAM WILL DISPLAY SECONDS FROM CLOCK IN*                                
* NIXIES AT-ONE SECOND INTERVALS• *                                
* LOCATION '6430 *                                
* INHIBIT ALARM TRANSMISSION TO CHICAGO *                                
** PROG WILL TST FOR FUNCT 72 AND VALID TIME**                                
* <MAX 120) IN SW8. IF BOTH VALID IT WILL *                                
* TURN ON ALARM INHIBIT LIGHT AND DISPLAY *                                
* DELAY TIME IN NIX WITH FUNCT 72• TIME IS * * TESTED IN SEC RATHER THAN MINUTES• *                                
* *                                 
     REL                            
     SPB  CRLF                      
*PRINT 60 CHAR PER LINE                                
     LAA  ='177717                  
     STA  CNTR                      
STRT NOP                            
     TEU  '40                       
*SET POINT EXEC                                
     DATA '100000                   
     BRU  SETP                      
     TEU  '40                       
* HI TEMP SHUT DOWN
     DATA '40000                   
     BRU  OFF                       
     TEU  '40                       
* HI TEMP WARNING
     DATA '20000                   
     BRU  *+2                       
     BRU  WARN                      
     TEU  '40                       
* ALARM RECALL
     DATA '10000                   
     BRU  RECL                      
     BRU  STRT                      
* PRINT S
SETP LAA  ='151400                 
     SPB  AOP                       
     MOP  '43,W                     
* RESET ST PT EXEC
     DATA '100000                  
     BRU  STRT                      
* PRINT 0
OFF  LAA  =' 147400                
     SPB  AOP                       
     BRU  STRT                      
* PRINT w
WARN LAA  ='153400                 
     SPB  AOP                       
     BRU  STRT                      
* PRINT R
RECL LAA  = '151000                
     SPB  AOP                       
     MOP  '43,W                     
* RESET ALARM RECALL
     DATA '4000                    
     BRU  STRT                      
AOP  HLT                            
* COUNTER F/DLY
     IMS  CNTA                     
* CHANGE TO BRU -1 F/DLY
     BRU  *+l                      
     AOP  1, W                      
     IMS  CNTR                      
     BRU* AOP                       
     LAA  ='177717                  
     STA  CNTR                      
     SPB  CRLF                      
     BRU* AOP                       
CRLF HLT                            
     MOP  1,w                       
     DATA '106400                   
     MOP  1,W                       
     DATA '105000                   
     BRU* CRLF                      
CNTR DATA 0                         
CNTA DATA 0                         
* **********************
     **** ********                 
     ORG  '200                      
* INPT SEC
     AIP  '40,W                    
* STORE F/COMPARE
     STA  CMPR                     
* INPT SEC
BEGN AIP  '40,w                    
     CMA  CMPR                      
     BRU  *+2                       
     BRU  BEGN                      
     STA  CMPR                      
* SETPOINT SW S8
     SNS  8                        
     BRU  STPT                      
* LEFT SW S5
     SNS  5                        
     BRU  LEFT                      
* CNTR SW S6
     SNS  6                        
     BRU  CNIX                      
* RIGHT SW S7
     SNS  7                        
     BRU  RITE                      
* INPT S5 LEFT SW
     AIP  '43,w                    
     LSL  4                         
     RSL  4                         
* DSPLA S5 IN L NIX
     AOP  '40,W                    
* INPT S6 CNTR SW
     AIP  '44,W                    
     RSL  8                         
* DSPLA S6 INC NIX
     AOP  '41, W                   
* INPT S7 RIGHT SW
     AIP  '44,W                    
     LSL  8                         
     RSL  8                         
* DISPLA S7 IN R NIX
     AOP  '42, W                   
     BRU  BEGN                      
STPT CLA                            
* CLR LEFT NIX
     AOP  '40,W                    
* INPT S8 SETPT SW
     AIP  '45,W                    
* DSPLA UTH S8 IN R NIX
     AQP  '42,W                    
     RSL  12                        
* DSPLA THOU OF S8 IN C NIX
     AOP  '41,W                    
     BRU  BEGN                      
LEFT CLA                            
* CLR C NIX
     AOP  '41,W                    
* CLR R NIX
     AOP  '42,W                    
* INPT 55
     AIP  '43,w                    
     LSL  4                         
     RSL  4                         
* OUPT TO L NIX
     AOP  '40,W                    
     BRU  BEGN                      
CNIX CLA                            
* CLR L NIX
     AOP  '40,W                    
* CLR R NIX
     AOP  '42,W                    
* INPT S6
     AIP  '44,W                    
     RSL  8                         
* OUPT TO C NIX
     AOP  '41,W                    
     BRU  BEGN                      
RITE CLA                            
* CLR L NIX
     AOP  '40,W                    
* CLR C N1X
     AOP  '41,W                    
* INPT S7
     AIP  '44,w                    
     LSL  8                         
     RSL  8                         
* OUPT TOR NIX
     AOP  '42,w                    
     BRU  BEGN                      
CMPR DATA 0                         
* ***********************
     **** ********                 
     ORG  '400                      
* INPUT SEC
     AIP  '40,w                    
* SAVE UNITS ONLY
     LSL  12                       
* STA F/COMPARE
     STA  DATA                     
BIGN AIP  '40,W                     
     LSL  12                        
* CK F/1 SEC CHNG
     CMA  DATA                     
     BRU  *+2                       
* WAIT F/NXT SEC
     BRU  BIGN                     
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
* ***********************
     **** ********                 
     ORG  '430                      
     CLA                            
     STA  LOCA                      
     BRU  RSET                      
HOME IMS  LOCC                      
     BRU  *-1                       
     TEU  '40                       
* SET PT EXEC
     DATA '100000                  
     BRU  *+2                       
     BRU  HOME+2                    
* SW 7
     A.IP '44,W                    
* SHIFT SW6 OFF
     LSL  8                        
* SW7=FUNCT 72
     CMA  ='71000                  
     BRU  *+2                       
     BRU  *+9                       
* WRONG FNCT NO
     SPB  FNCT                     
RSET LAA  ='100000                  
* RESET SET PT
     AOP  '43,W                    
     CLA                            
     AOP  '40,W                     
* CLR NIX
     AOP  '41,W                    
* CLR N!X
     AOP  '42,W                    
     BRU  HOME                      
* SW8 F/INHIBIT TIME
     AIP  '45,W                    
     STA  LOCB                      
* ADD F/INQUISITIVE TECHN
     SAS                           
     BRU  EROR                      
     BRU  *+1                       
     BRU  *+1                       
* TIME MORE THAN 120
     CMA  ='440                    
     BRU  *+1                       
* ='440 OR 120
     BRU  *+3                      
EROR SPB  SORY ·                   
     BRU  RSET                      
     LAA  ='101000                  
* RSET ST PT-TRN ON LIGHT
     AOP  '43,W                    
     LAA  LOCB                      
     BRU  *+3                       
AGAN LAA  LOCB                      
* SUBT 1 F/CNT
     SMA  =!                       
     STA  LOCB                      
     SAZ                            
     BRU  *+2                       
* TRN OFF LIGHT
     BRU  OFFF                     
     LSL  8                         
* CK F/INVALID BCD
     CMA  ='177400                 
     BRU  *+2                       
* SUBT '146
     BRU  SUBX                     
     LSL  4                         
* CK F/INVALID BCD
     CMA  ='170000                 
     BRU  *+2                       
* SUBT 6
     BRU  SUB6                     
AOPP NOP                            
* LFT NIX
     AlP  '43,w                    
     LSL  8                         
     SMA  ='071000                  
     SAZ                            
     BRU  *+2                       
     BRU  A40                       
     CLA                            
* CLR NIX
     AOP  '40,W                    
     BRU  *+3                       
A40  LAA  LOCB                      
     AOP  '40,W                     
* CNTR NIX
     AIP  '44,W                    
     RSL  8                         
     SMA  ='162                     
     SAZ                            
     BRU  *+2                       
     BRU  A41                       
     CLA                            
* CLR NIX
     AOP  '41,W                    
     BRU  *+3                       
A41  LAA  LOCB                      
     AOP  '41,W                     
* RT NIX
     AIP  '44,W                    
     LSL  8                         
     SMA  ='071000                  
     SAZ                            
     BRU  *+2                       
     BRU  A42                       
     CLA                            
* CLR NIX
     AOP  '42,W                    
     BRU  *+3                       
A42  LAA  LOCB                      
     AOP  '42,w                     
     LAA  LOCA                      
     SAZ                            
     BRU  TIME                      
* INPT SEC
     AIP  '40,W                    
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
* SUBT '146
SUBX LAA  LOCB                     
     SMA  =' 146                    
     STA  LOCB                      
     BRU  AOPP                      
* SUBT 6
SUB6 LAA  LOCB                     
     SMA  =6                        
     STA  LOCB                      
     BRU  AOPP                      
* TRN OFF LITE, CLR NIX
OFFF CLA                           
     AOP  '40,W                     
     AOP  '41,W                     
     AOP  '42,W                     
     AOP  '43,w                     
     SPB  RESM                      
     BRU  RSET                      
* CNT IN SW 8 OVER 120
SORY HLT                           
     SPB  CRLF                      
     LBA  =-18                      
     LAA  TBLA+18,1                 
     SPB  TTY                       
     IBS                            
     BRU  *-3                       
     BRU* SORY                      
* SW 7 NOT 72
FNCT HLT                           
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
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
TBLC DATA ''ALARMS WILL BE TRANSMITTED TO CHICAGO" 
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
     END                            
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
