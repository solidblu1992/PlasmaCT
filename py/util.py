#from bn128_curve import *
from optimized_curve_algorithms import *
from optimized_curve_cofactor import *
import sha3

#alt_bn_128 curve parameters
Ncurve = curve_order
Pcurve = field_modulus
counters = [0]*32
use_simple_hash_to_point = True

def sqrt(x):
    if ((type(x) != FQ) and (type(x) != FQ2)):
        x = FQ(x)

    if (type(x) == FQ):
        x0 = x**((Pcurve+1)//4)
        if (x == x0**2):
            return x0
        else:
            return FQ.zero()
    else:
        q = Pcurve
        a1 = x**((q-3)//4)
        alpha = a1*a1*x
        a0 = (alpha**q)*alpha #alpha**(q+1)

        if (a0 == FQ2([Pcurve-1,0])):
            return FQ2.zero()

        x0 = a1*x

        if (alpha == FQ2([Pcurve-1,0])):
            return FQ2([0,1])*x0
        else:
            b = (alpha + FQ2.one())**((q-1)//2)
            return b*x0
              
def bytes_to_int(b):
    result = 0

    for byte in b:
        result = result * 256 + int(byte)

    return result

def int_to_iterable(i):
	x = []
	bits = 0
	while i > 0:
		y = i & (0xFF << bits)
		x = [(y >> bits)] + x
		i = i - y
		bits = bits + 8

	return x

def int_to_bytes(i, N=32):
	x = bytes(int_to_iterable(i % ((1<<8*N)-1)))
	if (len(x) < N):
		y = bytes(N - len(x))
		x = y+x

	return x

def bytes_to_str(b):
    s = "0x"
    for i in range(0, len(b)):
        s_new = hex(b[i])[2:]
        if (len(s_new) < 2):
            s += "0" + s_new
        else:
            s += s_new

    return s

def point_to_bytes(p):
    if (len(p) > 2):
        p = normalize(p)
        
    if (type(p[0]) == FQ):
        data = [int_to_bytes(p[0].n, 32), int_to_bytes(p[1].n, 32)]
    else:
        data = [[int_to_bytes(p[0].coeffs[0],32),
                 int_to_bytes(p[0].coeffs[1],32)],
                [int_to_bytes(p[1].coeffs[0],32),
                 int_to_bytes(p[1].coeffs[1],32)]]

    return data

def bytes_to_point(b):
    assert(type(b) == list)
    assert(len(b) == 2)

    if (type(b[0]) != list):
        P = (FQ(bytes_to_int(b[0])),
             FQ(bytes_to_int(b[1])),
             FQ(1))
    else:
        P = (FQ2([bytes_to_int(b[0][0]), bytes_to_int(b[0][1])]),
             FQ2([bytes_to_int(b[1][0]), bytes_to_int(b[1][1])]),
             FQ2([1, 0]))
        
    return P

def str_to_bytes(msg):
    return bytes(msg, 'UTF-8')

def point_to_str(p):
    if (type(p) != tuple):
        p = ExpandPoint(p)

    if (len(p) == 3):
        p = normalize(p)

    if (type(p[0]) == FQ):
        s = (bytes_to_str(int_to_bytes(p[0].n, 32)) + ",\n" + bytes_to_str(int_to_bytes(p[1].n, 32)))
    else:
        s = "[" + bytes_to_str(int_to_bytes(p[0].coeffs[0], 32)) + ",\n" + bytes_to_str(int_to_bytes(p[0].coeffs[1], 32)) + "],\n["
        s += bytes_to_str(int_to_bytes(p[1].coeffs[0], 32)) + ",\n" + bytes_to_str(int_to_bytes(p[1].coeffs[1], 32)) + "]"
    return s

def point_to_str_packed(p):
    if (type(p) != tuple):
        p = ExpandPoint(p)

    if (len(p) == 3):
        p = normalize(p)

    if (type(p[0]) == FQ):
        s = bytes_to_str(int_to_bytes(p[0].n, 32))[2:] + bytes_to_str(int_to_bytes(p[1].n, 32))[2:]
    else:
        s = bytes_to_str(int_to_bytes(p[0].coeffs[0], 32))[2:] + bytes_to_str(int_to_bytes(p[0].coeffs[1], 32))[2:]
        s += bytes_to_str(int_to_bytes(p[1].coeffs[0], 32))[2:] + bytes_to_str(int_to_bytes(p[1].coeffs[1], 32))[2:]
                         
    return s

def hash_of_int(i):
    hasher = sha3.keccak_256(int_to_bytes(i,32))
    x = bytes_to_int(hasher.digest())
    return x

def hash_of_str(s):
    hasher = sha3.keccak_256(bytes(s, "UTF-8"))
    x = bytes_to_int(hasher.digest())
    return x

def get_xy1(x_1, x_2, x_3):
    #Check x_1
    y2 = x_1**3 + b
    y = sqrt(y2)

    if (y != FQ.zero()):
        return (x_1, y, FQ.one())

    #Check x_2
    y2 = x_2**3 + b
    y = sqrt(y2)

    if (y != FQ.zero()):
        return (x_2, y, FQ.one())

    #Check x_3
    y2 = x_3**3 + b
    y = sqrt(y2)
    assert(y != FQ.zero())
    return (x_3, y, FQ.one())

def get_xy2(x_1, x_2, x_3):
    #Check x_1
    y2 = x_1**3 + b2
    y = sqrt(y2)

    if (y != FQ2.zero()):
        return (x_1, y, FQ2.one())

    #Check x_2
    y2 = x_2**3 + b2
    y = sqrt(y2)

    if (y != FQ2.zero()):
        return (x_2, y, FQ2.one())

    #Check x_3
    y2 = x_3**3 + b2
    y = sqrt(y2)
    assert(y != FQ2.zero())
    return (x_3, y, FQ2.one())

def point1_from_t(t):
    if (type(t) != FQ):
        t = FQ(t)

    #Simple hash to point
    #t = x-coordinate, check if x is on curve
    #if not, increment t by 1
    if (use_simple_hash_to_point):
        x = t

        onCurve = False
        while (not onCurve):
            y2 = x**3 + b
            y = sqrt(y2)

            onCurve = (y**2 == y2)

            if (not onCurve):
                x += 1
        
        return (x, y, FQ.one())

    #More complex hash to point
    #Only has to check 3 x-cordinates at most
    else:
        sqrt3 = sqrt(FQ(-3))
        F0 = ((sqrt3-1)/2, sqrt(1+b), FQ(1))

        if (t == 0):
            return F0
        
        w = sqrt3*t/(1+b+t**2)
        x_1 = (sqrt3-1)/2 - t*w
        x_2 = -x_1 - 1
        x_3 = 1 + 1 / w**2

        T = get_xy1(x_1, x_2, x_3)

        return add(F0, T)
    

def point2_from_t(t):  
    if (type(t) != FQ2):
        t = FQ2([t, hash_of_int(t)])

    #Simple hash to point
    #t = x-coordinate, check if x is on curve
    #if not, increment t by [1, 0]
    if (use_simple_hash_to_point):
        x = t

        onCurve = False
        while (not onCurve):
            y2 = x**3 + b2
            y = sqrt(y2)#y2**a

            onCurve = (y**2 == y2)

            if (not onCurve):
                x += FQ2([1, 0])
        
        return multiply((x, y, FQ2.one()), Fp2_cofactor)
    
    #More complex hash to point
    #Only has to check 3 x-cordinates at most
    else:  
        sqrt3 = sqrt(FQ2([-3, 0]))
        F0 = ((sqrt3-FQ2.one())/2, sqrt(FQ2.one()+b2), FQ2.one())

        if (t == FQ2.zero()):
            return F0

        w = sqrt3*t/(FQ2.one()+b2+t**2)

        x_1 = (sqrt3-FQ2.one())/FQ2([2, 0]) - t*w
        x_2 = -x_1 - FQ2.one()
        x_3 = FQ2.one() + FQ2.one() / w**2

        T = get_xy2(x_1, x_2, x_3)

        return multiply(add(F0, T), Fp2_cofactor)
    

def hash_of_point(p):
    p = normalize(p)
    hasher = sha3.keccak_256()

    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes(p[0].n, 32))
        hasher.update(int_to_bytes(p[1].n, 32))
    else:
        hasher.update(int_to_bytes(p[0].coeffs[0], 32))
        hasher.update(int_to_bytes(p[0].coeffs[1], 32))
        hasher.update(int_to_bytes(p[1].coeffs[0], 32))
        hasher.update(int_to_bytes(p[1].coeffs[1], 32))
        
    x = bytes_to_int(hasher.digest())
    return x

def hash_addr_to_point1(addr):
    hasher = sha3.keccak_256(int_to_bytes(addr, 20) + b"G1")
    x = bytes_to_int(hasher.digest())
    return point1_from_t(x)

def hash_addr_to_point2(addr):
    hasher = sha3.keccak_256(int_to_bytes(addr, 20) + b"G2_0")
    c_0 = bytes_to_int(hasher.digest())
    hasher = sha3.keccak_256(int_to_bytes(addr, 20) + b"G2_1")
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])
    return point2_from_t(t)

def hash_int_to_point1(addr):
    hasher = sha3.keccak_256(int_to_bytes(addr, 32) + b"G1")
    x = bytes_to_int(hasher.digest())
    return point1_from_t(x)

def hash_int_to_point2(addr):
    hasher = sha3.keccak_256(int_to_bytes(addr, 32) + b"G2_0")
    c_0 = bytes_to_int(hasher.digest())
    hasher = sha3.keccak_256(int_to_bytes(addr, 32) + b"G2_1")
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])
    return point2_from_t(t)

def hash_str_to_point1(s):
    hasher = sha3.keccak_256(bytes(s + "G1", "UTF-8"))
    x = bytes_to_int(hasher.digest())
    return point1_from_t(x)

def hash_str_to_point2(s):
    hasher = sha3.keccak_256(bytes(s + "G2_0", "UTF-8"))
    c_0 = bytes_to_int(hasher.digest())
    hasher = sha3.keccak_256(bytes(s + "G2_1", "UTF-8"))
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])
    return point2_from_t(t)

def hash_point_to_point1(p):
    p = normalize(p)
    hasher = sha3.keccak_256()

    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes(p[0].n, 32))
        hasher.update(int_to_bytes(p[1].n, 32))
    else:
        hasher.update(int_to_bytes(p[0].coeffs[0], 32))
        hasher.update(int_to_bytes(p[0].coeffs[1], 32))
        hasher.update(int_to_bytes(p[1].coeffs[0], 32))
        hasher.update(int_to_bytes(p[1].coeffs[1], 32))
        
    hasher.update(b"G1")
    x = bytes_to_int(hasher.digest())    
    return point1_from_t(x)

def hash_point_to_point2(p):
    p = normalize(p)

    hasher = sha3.keccak_256()
    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes(p[0].n, 32))
        hasher.update(int_to_bytes(p[1].n, 32))
    else:
        hasher.update(int_to_bytes(p[0].coeffs[0], 32))
        hasher.update(int_to_bytes(p[0].coeffs[1], 32))
        hasher.update(int_to_bytes(p[1].coeffs[0], 32))
        hasher.update(int_to_bytes(p[1].coeffs[1], 32))
    hasher.update(b"G2_0")
    c_0 = bytes_to_int(hasher.digest())

    hasher = sha3.keccak_256()
    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes(p[0].n, 32))
        hasher.update(int_to_bytes(p[1].n, 32))
    else:
        hasher.update(int_to_bytes(p[0].coeffs[0], 32))
        hasher.update(int_to_bytes(p[0].coeffs[1], 32))
        hasher.update(int_to_bytes(p[1].coeffs[0], 32))
        hasher.update(int_to_bytes(p[1].coeffs[1], 32))
    hasher.update(b"G2_1")
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])   
    return point2_from_t(t)

def add_point_to_hasher(hasher, p):
    p = normalize(p)

    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes(p[0].n, 32))
        hasher.update(int_to_bytes(p[1].n, 32))
    else:
        hasher.update(int_to_bytes(p[0].coeffs[0], 32))
        hasher.update(int_to_bytes(p[0].coeffs[1], 32))
        hasher.update(int_to_bytes(p[1].coeffs[0], 32))
        hasher.update(int_to_bytes(p[1].coeffs[1], 32))
        
    return hasher

#Definition of H = hash_point_to_point(G)
H = hash_point_to_point1(G)

def GetAssetH(addr):
    return hash_addr_to_point(addr)

def KeyImage(xk):
    return multiply(hash_to_point(multiply(G,xk)), xk)

#Utility Functions
def CompressPoint(Pin):
    if (type(Pin) != tuple):
        return Pin
    
    Pin = normalize(Pin)
    Pout = Pin[0].n
    if ( (Pin[1].n & 0x1) == 0x1):
        Pout = Pout | (0x3 << 256)
    else:
        Pout = Pout | (0x2 << 256) 

    return Pout

def ExpandPoint(Pin):
    import math

    parity = (Pin & (0x3 << 256)) >> 256
    assert (parity == 0x2 or parity == 0x3)
    
    x = Pin & 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    y_squared = x**3 + b
    y = y_squared**((Pcurve+1)//4)

    if (parity == 0x2):
        if ( (y.n & 0x1) == 0 ):
            Pout = (FQ(x), FQ(y), FQ(1))
        else:
            Pout = (FQ(x), FQ(Pcurve-y), FQ(1))
    else:
        if ( (y.n & 0x1) == 0 ):
            Pout = (FQ(x), FQ(Pcurve-y), FQ(1))
        else:
            Pout = (FQ(x), FQ(y), FQ(1))

    return Pout

def getRandom(count=1, bits=254, modulus=Ncurve):
    import random

    if (count == 1):
        out = random.SystemRandom().getrandbits(bits)

        if (modulus > 0):
            out = out % modulus
    else:
        out = []

        if (modulus > 0):
            for i in range(0, count):
                out += [random.SystemRandom().getrandbits(bits) % modulus]
        else:
            for i in range(0, count):
                out += [random.SystemRandom().getrandbits(bits)]
            

    return out


def getRandomUnsafe(seed=None):
    import random
    if (seed != None):
        random.seed(seed)
        
    out = (random.getrandbits(254) % Ncurve)

    return out

def ExpandCompressTest():
    for i in range(0, 20):
        x = getRandom()
        point = multiply(G, x)
        cpoint = CompressPoint(point)
        point2 = ExpandPoint(CompressPoint(point))
    
        print("Test[" + str(i) + "]...", end="")
        if (not eq(point, point2)):
            print("Failure! ", end="")

            if ((point[1].n & 0x1) == 0x1):
                print("point is odd")
            
            #print("point = " + hex(point[0].n))
            #print("cpoint = " + hex(cpoint))
        else:
            print("Success!")

def sNeg(a):
    return (Ncurve - (a % Ncurve)) % Ncurve

def sAdd(a, b):
    return (a + b) % Ncurve

def sSub(a, b):
    return sAdd(a, sNeg(b))

def sMul(a, b, modulus=Ncurve):
    return (a * b) % modulus

def sSq(a):
    return sMul(a, a)

def sPow(a, p, modulus=Ncurve):     
    return pow(a, p, modulus)

def sInv(a, modulus=Ncurve):
    a = a % modulus
    assert(a > 0)

    t1 = 0
    t2 = 1
    r1 = modulus
    r2 = a
    q = 0
    while (r2 != 0):
        q = r1 // r2
        (t1, t2, r1, r2) = (t2, t1 - q*t2, r2, r1 - q*r2)

    if (t1 < 0):
        t1 = t1 % modulus

    assert(sMul(a, t1, modulus) == 1)
    return t1

def sDiv(a, b, modulus=Ncurve):
    return sMul(a, sInv(b, modulus), modulus)

def vPow(x, N):
    if (x == 0):
        return [0]*N
    elif (x == 1):
        return [1]*N

    out = [0]*N
    out[0] = 1
    for i in range(1, N):
        out[i] = sMul(out[i-1], x)

    return out

def vSum(a):
    out = a[0]
    for i in range(1, len(a)):
        out = sAdd(out, a[i])

    return out

def vAdd(a, b):
    assert(len(a) == len(b))

    out = [0]*len(a)
    for i in range(0, len(a)):
        out[i] = sAdd(a[i], b[i])

    return out

def vSub(a, b):
    assert(len(a) == len(b))

    out = [0]*len(a)
    for i in range(0, len(a)):
        out[i] = sSub(a[i], b[i])

    return out

def vMul(a, b):
    assert(len(a) == len(b))

    out = [0]*len(a)
    for i in range(0, len(a)):
        out[i] = sMul(a[i], b[i])

    return out

def vScale(a, s):
    out = [0]*len(a)
    for i in range(0, len(a)):
        out[i] = sMul(a[i], s)

    return out
    
def vDot(a, b):
    assert(len(a) == len(b))

    out = 0
    for i in range(0, len(a)):
        out = sAdd(out, sMul(a[i], b[i]))

    return out

def vSlice(a, start, stop):
    out = [0]*(stop-start)

    for i in range(start, stop):
        out[i-start] = a[i]

    return out

