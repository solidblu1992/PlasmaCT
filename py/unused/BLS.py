from util import *
from optimized_pairing import *

#Class that creates and verifies signatures for blank messages (M = G2)
class BLS:
    def __init__(self, P, S):
        self.P = P
        self.S = S

    def sign(x):
        S = multiply(G2, x)
        P = multiply(G, x)
        return BLS(P, S)

    def verify(self):
        return (pairing(self.S, G) == pairing(G2, self.P))

    def aggregate(bls_sigs):
        P = bls_sigs[0].P
        S = bls_sigs[0].S
        for i in range(1, len(bls_sigs)):
            P = add(P, bls_sigs[i].P)
            S = add(S, bls_sigs[i].S)
            
        return BLS(P, S)

class BLSHardened:
    def __init__(self, P, S, Psq):
        self.P = P
        self.S = S
        self.Psq = Psq

    def sign(x):
        S = multiply(G2, x)
        P = multiply(G, x)
        Psq = multiply(G, sSq(x))
        return BLSHardened(P, S, Psq)

    def verify(self):
        if (pairing(self.S, G) != pairing(G2, self.P)):
            return False

        if (pairing(self.S, self.P) != pairing(G2, self.Psq)):
            return False

        return True

    def aggregate(bls_sigs):
        P = bls_sigs[0].P
        S = bls_sigs[0].S
        Psq = bls_sig[0].Psq
        
        for i in range(1, len(bls_sigs)):
            P = add(P, bls_sigs[i].P)
            S = add(S, bls_sigs[i].S)
            Psq = bls_sig[0].Psq
            
        return BLSHardened(P, S, Psq)
    
if (False):
    x = getRandom(10)
    sigs = []
    for i in range(0, len(x)):
        sigs.append(BLS.sign(x[i]))
        
    sig_agg = BLS.aggregate(sigs)

    import time
    ms = time.time()
    sig_agg.verify()
    t = time.time()-ms

if (True):
    x = getRandom()
    P = multiply(G, x)
    S = multiply(G2, x)
    
    x2 = sSq(x)
    P2 = multiply(G, x2)
    S2 = multiply(G2, x2)
    
    x3 = sPow(x, 3)
    P3 = multiply(G, x3)
    S3 = multiply(G2, x3)

    
