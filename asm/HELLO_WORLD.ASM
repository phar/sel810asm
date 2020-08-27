*     REL
     SPB  PRNT
     HLT
TTY  HLT
     AOP  1,W
     LSL  8
     AOP  1,W
     BRU* TTY
CRLF HLT
     MOP  1,W
     DATA '106400
     MOP  1,W
     DATA '105000
     BRU* CRLF
PRNT HLT
     SPB  CRLF
     LBA  =-6
     LAA  TBLA+6,1
     SPB  TTY
     IBS
     BRU  *-3
     BRU* PRNT
TBLA DATA ''HELLO WORLD!''
