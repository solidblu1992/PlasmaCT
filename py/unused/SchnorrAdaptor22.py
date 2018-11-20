from util import *
from sha3 import *
from optimized_curve import *

class SchnorrAdaptor22:
    def __init__(self, P, R, T, sp, msg="", t=None):
        self.P = P
        self.R = R
        self.T = T
        self.sp = sp
        self.msg = msg
        self.t = t

    #Calculate joint key for public keys Pa and Pb
    def calc_J(Pa, Pb):
        hasher = sha3.keccak_256()
        hasher = add_point_to_hasher(hasher, Pa)
        hasher = add_point_to_hasher(hasher, Pb)
        hash_ab = bytes_to_int(hasher.digest())

        hasher = sha3.keccak_256(int_to_bytes(hash_ab, 32))
        hasher = add_point_to_hasher(hasher, Pa)
        hash_ab_a = bytes_to_int(hasher.digest())

        hasher = sha3.keccak_256(int_to_bytes(hash_ab, 32))
        hasher = add_point_to_hasher(hasher, Pb)
        hash_ab_b = bytes_to_int(hasher.digest())

        J = shamir([Pa, Pb], [hash_ab_a, hash_ab_b])
        return J
    
    def calc_e(msg, J, Ra, Rb, T):
        hasher = sha3.keccak_256()
        hasher = add_point_to_hasher(hasher, J)
        hasher = add_point_to_hasher(hasher, add(add(Ra, Rb), T))
        
        if (msg == ""):
            hasher = sha3.keccak_256(b"\x00")
        else:
            hasher = sha3.keccak_256(str_to_bytes(msg))
        
        e = bytes_to_int(hasher.digest())
        return e
    
    #Create Schnorr Adaptor Signature
    def sign_step1a_alice(xa):
        ra = getRandom()

        Pa = multiply(G, xa)
        Ra = multiply(G, ra)

        return ((Pa, Ra), (xa, ra))   #Only send argument 0 to bob

    def sign_step1b_bob(xb):
        rb = getRandom()
        t = getRandom()
        
        Pb = multiply(G, xb)
        Rb = multiply(G, rb)
        T = multiply(G, t)

        return ((Pb, Rb, T), (xb, rb, t)) #Only send argument 0 to alice

    def sign_step2a_bob(step1a_alice, step1b_bob):
        #Create adaptor signature for Alice
        Pa, Ra = step1a_alice
        Pb, Rb, T = step1b_bob[0]
        xb, rb, null = step1b_bob[1] #t not needed here
        
        J = SchnorrAdaptor.calc_J(Pa, Pb)
        e = SchnorrAdaptor.calc_e(J, Ra, Rb, T)

        sp = sSub(rb, sMul(e, xb))
        return sp

    def sign_step2b_alice(step1a_alice, step1b_bob,
                          step2a_bob):
        #Validate Bob's adaptor signature
        #i.e. it would be valid if alice knew t
        Pa, Ra = step1a_alice[0]
        xa, ra = step1a_alice[1]
        Pb, Rb, T = step1b_bob
        sp = step2a_bob

        J = SchnorrAdaptor.calc_J(Pa, Pb)
        e = SchnorrAdaptor.calc_e(J, Ra, Rb, T)

        Sp = multiply(G, sp)
        Right = add(Rb, multiply(Pb, sNeg(e)))
        assert (eq(Sp, Right))

        #Create Alice's portion of the 2 of 2 for Bob
        sa = sSub(ra, sMul(e, xa))
        return sa

    def sign_step3a_bob(step1a_alice, step1b_bob,
                        step2a_bob, step2b_alice):
        Pa, Ra = step1a_alice
        Pb, Rb, T = step1b_bob[0]
        xb, rb, t = step1b_bob[1]
        sa = step2b_alice

        J = SchnorrAdaptor.calc_J(Pa, Pb)
        e = SchnorrAdaptor.calc_e(J, Ra, Rb, T)
        
        sb = sSub(sAdd(rb, t), sMul(e, xb))
        s_agg = sAdd(sa, sb)
        return s_agg

    def sign_step3b_alice(step1a_alice, step1b_bob,
                          step2a_bob, step2b_alice,
                          step3a_bob):
        Pa, Ra = step1a_alice[0]
        xa, ra = step1a_alice[1]
        Pb, Rb, T = step1b_bob
        sp = step2a_bob
        sa = step2b_alice
        s_agg = step3a_bob

        t = sSub(s_agg, sAdd(sa, sp))
        return t
        
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
    
