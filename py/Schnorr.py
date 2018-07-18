from util import *
from sha3 import *
from optimized_curve import *

class Schnorr:
    msg = ""
    R = NullPoint
    s = 0

    def __init__(self, R, s, msg=""):
        self.R = R
        self.s = s
        self.msg = msg

    #Create Schnorr Signature
    def sign(private_key, msg=""):
        r = getRandom()
        R = multiply(G1, r);
        hasher = sha3.keccak_256()
        hasher = add_point_to_hasher(hasher, R)
        hasher.update(str_to_bytes(msg))
        e = bytes_to_int(hasher.digest())
        s = sSub(r, sMul(private_key, e))
        
        return Schnorr(R, s, msg)

    #Verify Schnorr Signature
    def verify(self):
        hasher = sha3.keccak_256()
        hasher = add_point_to_hasher(hasher, self.R)
        hasher.update(str_to_bytes(self.msg))
        e = bytes_to_int(hasher.digest())

        S = multiply(G1, self.s)
        PubKey = multiply(add(self.R, neg(S)), sInv(e))

        Rp = shamir([G1, PubKey], [self.s, e])
        
        return eq(self.R, Rp)

    #Get signer's public key
    def recover(self):
        hasher = sha3.keccak_256()
        hasher = add_point_to_hasher(hasher, self.R)
        hasher.update(str_to_bytes(self.msg))
        e = bytes_to_int(hasher.digest())

        S = multiply(G1, self.s)
        PubKey = multiply(add(self.R, neg(S)), sInv(e))
        return PubKey

    #Print Schnorr signature
    def print(self):
        print("Schnorr Signature:")
        print("msg: \"" + self.msg + "\"") 
        print("R: " + bytes_to_str(CompressPoint(self.R)))
        print("s: " + bytes_to_str(self.s))
        print("P: " + bytes_to_str(CompressPoint(self.recover())))

#Quick Test
if (False):
    x = getRandom()
    P = multiply(G1, x)
    sig = Schnorr.sign(x)
    if (sig.verify()):
        print("Signature valid!")
    else:
        print("Signature invalid!")
    sig.print()
