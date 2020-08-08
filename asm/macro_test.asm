WAIT MACR
@1   NOP
     NOP
     NOP
     BRU @1
     LAA =#1
     EMAC

    MWAIT '1
    MWAIT '2
    MWAIT '3
    END
