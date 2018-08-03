from util import *
from optimized_pairing import *

#Class that creates and verifies BLS signature
#Warning: BLS aggregation is careless and vulnerable to a rogue-key attack.  Shouldn't matter because this is being used for MimbleWimble
class BLS:
    def __init__(self, message, P, S):
        self.message = message
        self.P = P
        self.S = S

    def sign(x, message=""):
        M = hash_str_to_point2(message)
        S = multiply(M, x)
        P = multiply(G, x)
        return BLS(message, P, S)

    def verify(self):
        M = hash_str_to_point2(self.message)
        return (pairing(self.S, G) == pairing(M, self.P))

    def aggregate(bls_sigs):
        message = bls_sigs[0].message
        P = bls_sigs[0].P
        S = bls_sigs[0].S
        for i in range(1, len(bls_sigs)):
            assert(message == bls_sigs[i].message)
            P = add(P, bls_sigs[i].P)
            S = add(S, bls_sigs[i].S)
            
        return BLS(bls_sigs[0].message, P, S)

    def print(self):
        print("BLS Signature:")
        print("message: \"" + self.message + "\"")
        print("P:")
        print(point_to_str(self.P))
        print("S:")
        print(point_to_str(self.S))
    
if (True):
    x = getRandom(10)
    sigs = []
    for i in range(0, len(x)):
        sigs.append(BLS.sign(x[i]))
        
    sig_agg = BLS.aggregate(sigs)

    import time
    ms = time.time()
    sig_agg.verify()
    t = time.time()-ms

    
