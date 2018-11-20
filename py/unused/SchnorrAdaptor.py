from util import *
from sha3 import *
from optimized_curve import *

class SchnorrAdaptor:
    def __init__(self, P, R, T, sp, msg="", t=None):
        self.P = P
        self.R = R
        self.T = T
        self.sp = sp
        self.msg = msg
        self.t = t

    def calc_e(msg, P, R, T):
        hasher = sha3.keccak_256()
        hasher = add_point_to_hasher(hasher, P)
        hasher = add_point_to_hasher(hasher, add(R, T))
        
        if (msg == ""):
            hasher = sha3.keccak_256(b"\x00")
        else:
            hasher = sha3.keccak_256(str_to_bytes(msg))
        
        e = bytes_to_int(hasher.digest())
        return e

    #Create Schnorr Adaptor Signature
    def sign(private_key, msg=""):
        r = getRandom()
        t = getRandom()
        
        P = multiply(G, private_key)
        R = multiply(G, r)
        T = multiply(G, t)
        
        e = SchnorrAdaptor.calc_e(msg, P, R, T)
        sp = sSub(r, sMul(e, private_key))
        
        return SchnorrAdaptor(P, R, T, sp, msg, t)

    #Check to see of adaptor signature would be valid if t was known
    def validate(self):
        Sp = multiply(G, self.sp)

        e = SchnorrAdaptor.calc_e(self.msg, self.P, self.R, self.T)
        Right = add(self.R, multiply(self.P, sNeg(e)))

        return eq(Sp, Right)

    #Verify Schnorr Adaptor Signature
    #Knowledge of t is required here
    def verify(self, t=None):
        if (t == None):
            if (self.t == None):
                t = 0
            else:
                t = self.t
        
        S = multiply(G, sAdd(self.sp, t))

        e = SchnorrAdaptor.calc_e(self.msg, self.P, self.R, self.T)
        Right = add(add(self.R, self.T), multiply(self.P, sNeg(e)))
        
        return eq(S, Right)

    #Print Schnorr Adaptor Signature
    def print(self):
        print("Schnorr Adaptor Signature:")
        print("msg: \"" + self.msg + "\"") 
        print("P: " + bytes_to_str(int_to_bytes(CompressPoint(self.P), 32)))
        print("R: " + bytes_to_str(int_to_bytes(CompressPoint(self.R), 32)))
        print("T: " + bytes_to_str(int_to_bytes(CompressPoint(self.T), 32)))
        print("sp: " + bytes_to_str(int_to_bytes(self.sp, 32)))
        
#Quick Test
if (True):
    x = getRandom()
    sig = SchnorrAdaptor.sign(x)
    sig.print()

    validate_test = sig.validate()
    verify_test = sig.verify()
    
