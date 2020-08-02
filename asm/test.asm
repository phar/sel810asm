WAIT MACR
@1   NOP
     NOP
     NOP
     BRU @1
     LAA =#1
     EMAC

     DATA 1,2,3,4,5,6
     DATA 1                         comment
*formats supported in the reference..
*fixed point
*     DATA 23.456B10, -3B6,12C0
*floating point data
     DATA 22.3344E0, .12345D2
    MWAIT '1
    MWAIT '2
    MWAIT '3
     END
