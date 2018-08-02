from util import *
from sha3 import *
from optimized_curve import *

class Schnorr:
    def __init__(self, R, s, msg=""):
        self.R = R
        self.s = s
        self.msg = msg

    def calc_e(msg, R):
        if (msg == ""):
            hasher = sha3.keccak_256(b"\x00")
        else:
            hasher = sha3.keccak_256(str_to_bytes(msg))

        hasher = add_point_to_hasher(hasher, R)
        e = bytes_to_int(hasher.digest())
        return e

    #Create Schnorr Signature
    def sign(private_key, msg=""):
        r = getRandom()
        R = multiply(G, r);
        e = Schnorr.calc_e(msg, R)
        s = sSub(r, sMul(private_key, e))
        
        return Schnorr(R, s, msg)

    def sign_multiple(private_keys, msg=""):
        sigs = [None]*len(private_keys)
        for i in range(0, len(sigs)):
            sigs[i] = Schnorr.sign(private_keys[i], msg)

        return sigs

    #Verify Schnorr Signature
    def verify(self):
        e = Schnorr.calc_e(self.msg, self.R)
        S = multiply(G, self.s)
        PubKey = multiply(add(self.R, neg(S)), sInv(e))

        Rp = shamir([G, PubKey], [self.s, e])
        
        return eq(self.R, Rp)

    #Get signer's public key
    def recover(self):
        e = Schnorr.calc_e(self.msg, self.R)
        S = multiply(G, self.s)
        PubKey = multiply(add(self.R, neg(S)), sInv(e))
        return PubKey

    def recover_multiple(sigs):
        R = [NullPoint]*len(sigs)
        e_inv = [0]*len(sigs)
        Gscalar = 0

        for i in range(0, len(sigs)):
            R[i] = sigs[i].R

            if (sigs[i].msg == ""):
                hasher = sha3.keccak_256(b"\x00")
            else:
                hasher = sha3.keccak_256(str_to_bytse(sigs[i].msg))
                
            hasher = add_point_to_hasher(hasher, sigs[i].R)
            e_inv[i] = sInv(bytes_to_int(hasher.digest()))
            
            Gscalar = sAdd(sMul(sigs[i].s, e_inv[i]), Gscalar)

        #Recover Point
        PubKey = add(shamir_batch(R, e_inv), multiply(G, sNeg(Gscalar)))
        return PubKey
            

    #Print Schnorr signature
    def print(self):
        print("Schnorr Signature:")
        print("msg: \"" + self.msg + "\"") 
        print("R: " + bytes_to_str(CompressPoint(self.R)))
        print("s: " + bytes_to_str(self.s))
        print("P: " + bytes_to_str(CompressPoint(self.recover())))

    def print_eth(self):
        '''MEW:
        print("R:")
        print(point_to_str(self.R))
        print("s:")
        print(hex(self.s))
        print("W_sG:")
        print(point_to_str(multiply(G, self.s)))
        print("W_P:")
        print(point_to_str(self.recover()))
        '''
        print("\"0x0\",")
        R = normalize(self.R)
        print("[\"" + hex(R[0].n) + "\",")
        print("\"" + hex(R[1].n) + "\"],")
        print("\"" + hex(self.s) + "\",")
        print("\"" + hex(sInv(Schnorr.calc_e(self.msg, self.R))) + "\",")
        W_sG = normalize(multiply(G, self.s))
        print("[\"" + hex(W_sG[0].n) + "\",")
        print("\"" + hex(W_sG[1].n) + "\"],")
        P = normalize(self.recover())
        print("[\"" + hex(P[0].n) + "\",")
        print("\"" + hex(P[1].n) + "\"]")
        
#Quick Test
if (False):
    x = getRandom()
    P = multiply(G, x)
    
    sig = Schnorr.sign(x)
    Pout = normalize(sig.recover())

#Multiple Test
if (True):
    count = 5
    x = getRandom(count)
    P = normalize(shamir_batch([G]*count, x))

    sigs = Schnorr.sign_multiple(x)
    Pout = normalize(Schnorr.recover_multiple(sigs))
    
