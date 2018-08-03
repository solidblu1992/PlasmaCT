#from bn128_curve import *
from optimized_curve import *
import sha3

#alt_bn_128 curve parameters
Ncurve = curve_order
Pcurve = field_modulus
counters = [0]*32

useShamir = True    #Flag True to use Shamir's Trick to compute (a*A + b*B) effectively
useWindowed = True  #Flag True to use windowed EC Multiplication

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
        

def bytes_to_int(bytes):
    result = 0

    for b in bytes:
        result = result * 256 + int(b)

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

def int_to_bytes64(i):
    x = bytes(int_to_iterable(i% 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff))

    if (len(x) < 64):
        y = bytes(64 - len(x))
        x = y+x

    return x

def int_to_bytes32(i):
    x = bytes(int_to_iterable(i% 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff))

    if (len(x) < 32):
        y = bytes(32 - len(x))
        x = y+x

    return x

def int_to_bytes20(i):
    x = bytes(int_to_iterable(i% 0xffffffffffffffffffffffffffffffffffffffff))

    if (len(x) < 20):
        y = bytes(20 - len(x))
        x = y+x

    return x

def int_to_bytes16(i):
    x = bytes(int_to_iterable(i% 0xffffffffffffffffffffffffffffffff))

    if (len(x) < 16):
        y = bytes(16 - len(x))
        x = y+x

    return x

def to_point(x, y):
    return (FQ(x), FQ(y), FQ(1))

def bytes_to_str(b, N=32):
    s = hex(b)

    if (len(s) < (2*N+2)):
        y = (2*N+2) - len(s)
        y = "0" * y
        s = "0x" + y + s[2:]

    return s

def str_to_bytes(msg):
    return bytes(msg, 'UTF-8')

def point_to_str(p):
    if (type(p) != tuple):
        p = ExpandPoint(p)

    if (len(p) == 3):
        p = normalize(p)

    if (type(p[0]) == FQ):
        s = (bytes_to_str(p[0].n) + ",\n" + bytes_to_str(p[1].n))
    else:
        s = "[" + bytes_to_str(p[0].coeffs[0]) + ",\n" + bytes_to_str(p[0].coeffs[1]) + "],\n["
        s += bytes_to_str(p[1].coeffs[0]) + ",\n" + bytes_to_str(p[1].coeffs[1]) + "]"
    return s

def hash_of_int(i):
    hasher = sha3.keccak_256(int_to_bytes32(i))
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
    return (x_2, y, FQ.one())

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
        
    sqrt3 = sqrt(FQ(-3))
    F0 = ((sqrt3-1)/2, sqrt(1+b), FQ(1))

    if (t == 0):
        return F0
    
    w = sqrt3*t/(1+b+t**2)
    x_1 = (sqrt3-1)/2 - t*w
    x_2 = -x_1 - 1
    x_3 = 1 + 1 / w**2


    return x_1, x_2, x_3

    T = get_xy1(x_1, x_2, x_3)

    return add(F0, T)

def point2_from_t(t):
    if (type(t) != FQ2):
        t = FQ2([t, 0])

    sqrt3 = sqrt(FQ2([-3, 0]))
    F0 = ((sqrt3-FQ2.one())/2, sqrt(FQ2.one()+b2), FQ2.one())

    if (t == FQ2.zero()):
        return F0

    w = sqrt3*t/(FQ2.one()+b2+t**2)

    x_1 = (sqrt3-FQ2.one())/FQ2([2, 0]) - t*w
    x_2 = -x_1 - FQ2.one()
    x_3 = FQ2.one() + FQ2.one() / w**2

    T = get_xy2(x_1, x_2, x_3)

    return add(F0, T)

def hash_of_point(p):
    p = normalize(p)
    hasher = sha3.keccak_256()

    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes32(p[0].n))
        hasher.update(int_to_bytes32(p[1].n))
    else:
        hasher.update(int_to_bytes32(p[0].coeffs[0]))
        hasher.update(int_to_bytes32(p[0].coeffs[1]))
        hasher.update(int_to_bytes32(p[1].coeffs[0]))
        hasher.update(int_to_bytes32(p[1].coeffs[1]))
        
    x = bytes_to_int(hasher.digest())
    return x

def hash_addr_to_point1(addr):
    hasher = sha3.keccak_256(int_to_bytes20(addr) + b"G1")
    x = bytes_to_int(hasher.digest())
    return point1_from_t(x)

def hash_addr_to_point2(addr):
    hasher = sha3.keccak_256(int_to_bytes20(addr) + b"G2_0")
    c_0 = bytes_to_int(hasher.digest())
    hasher = sha3.keccak_256(int_to_bytes20(addr) + b"G2_1")
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])
    return point2_from_t(t)

def hash_int_to_point1(addr):
    hasher = sha3.keccak_256(int_to_bytes32(addr) + b"G1")
    x = bytes_to_int(hasher.digest())
    return point1_from_t(x)

def hash_int_to_point2(addr):
    hasher = sha3.keccak_256(int_to_bytes32(addr) + b"G2_0")
    c_0 = bytes_to_int(hasher.digest())
    hasher = sha3.keccak_256(int_to_bytes32(addr) + b"G2_1")
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])
    return point2_from_t(t)

def hash_str_to_point1(s):
    hasher = sha3.keccak_256(bytes(s, "UTF-8") + b"G1")
    x = bytes_to_int(hasher.digest())
    return point1_from_t(x)

def hash_str_to_point2(s):
    hasher = sha3.keccak_256(bytes(s, "UTF-8") + b"G2_0")
    c_0 = bytes_to_int(hasher.digest())
    hasher = sha3.keccak_256(bytes(s, "UTF-8") + b"G2_1")
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])
    return point2_from_t(t)

def hash_point_to_point1(p):
    p = normalize(p)
    hasher = sha3.keccak_256()

    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes32(p[0].n))
        hasher.update(int_to_bytes32(p[1].n))
    else:
        hasher.update(int_to_bytes32(p[0].coeffs[0]))
        hasher.update(int_to_bytes32(p[0].coeffs[1]))
        hasher.update(int_to_bytes32(p[1].coeffs[0]))
        hasher.update(int_to_bytes32(p[1].coeffs[1]))
        
    hasher.update(b"G1")
    x = bytes_to_int(hasher.digest())    
    return point1_from_t(x)

def hash_point_to_point2(p):
    p = normalize(p)

    hasher = sha3.keccak_256()
    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes32(p[0].n))
        hasher.update(int_to_bytes32(p[1].n))
    else:
        hasher.update(int_to_bytes32(p[0].coeffs[0]))
        hasher.update(int_to_bytes32(p[0].coeffs[1]))
        hasher.update(int_to_bytes32(p[1].coeffs[0]))
        hasher.update(int_to_bytes32(p[1].coeffs[1]))
    hasher.update(b"G2_0")
    c_0 = bytes_to_int(hasher.digest())

    hasher = sha3.keccak_256()
    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes32(p[0].n))
        hasher.update(int_to_bytes32(p[1].n))
    else:
        hasher.update(int_to_bytes32(p[0].coeffs[0]))
        hasher.update(int_to_bytes32(p[0].coeffs[1]))
        hasher.update(int_to_bytes32(p[1].coeffs[0]))
        hasher.update(int_to_bytes32(p[1].coeffs[1]))
    hasher.update(b"G2_1")
    c_1 = bytes_to_int(hasher.digest())
    t = FQ2([c_0, c_1])   
    return point2_from_t(t)

def add_point_to_hasher(hasher, p):
    p = normalize(p)

    if (type(p[0]) == FQ):
        hasher.update(int_to_bytes32(p[0].n))
        hasher.update(int_to_bytes32(p[1].n))
    else:
        hasher.update(int_to_bytes32(p[0].coeffs[0]))
        hasher.update(int_to_bytes32(p[0].coeffs[1]))
        hasher.update(int_to_bytes32(p[1].coeffs[0]))
        hasher.update(int_to_bytes32(p[1].coeffs[1]))
        
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
    
    print(hex(parity))
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

def getRandom(count=1):
    import random

    if (count == 1):
        out = (random.SystemRandom().getrandbits(254) % Ncurve)
    else:
        out = []
        for i in range(0, count):
            out = out + [random.SystemRandom().getrandbits(254) % Ncurve]

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

#Elliptic Curve Multiplication
if (useWindowed):
    def precompute_points(P, wBits=5):        
        #Calculate Precompiled Points: [1, 3, 5, ...]*P
        wPowOver4 = 1 << (wBits-2)
        P_pre = [None]*wPowOver4
        P_pre[0] = P
        P2 = double(P)
        
        for i in range(1, len(P_pre)):
            P_pre[i] = add(P_pre[i-1], P2)

        return P_pre
    
    G_pre = precompute_points(G)
    H_pre = precompute_points(H)
    #G2_pre = precompute_points(G2)
    
    def multiply(P, s, wBits=5):
        wPow = (1 << wBits)
        wPowOver2 = wPow // 2

        if (type(P[0]) == FQ):
            Q = NullPoint
                    
            if (eq(P, G)):
                P_pre = G_pre
            elif (eq(P, H)):
                P_pre = H_pre
            else:
                P_pre = precompute_points(P, wBits)
        else:
            Q = NullPoint2
            
            if (eq(P, G2)):
                P_pre = G2_pre
        
        #Get NAF digits
        dj = []
        i = 0
        while (s > 0):
            if (s % 2) == 1:
                d = s % wPow
                if (d > wPowOver2):
                    d = d - wPow
                    
                s -= d
                
                dj += [d]
            else:
                dj += [0]

            s = s // 2
            i = i + 1

        for j in reversed(range(0, i)):
            Q = double(Q)
            if (dj[j] > 0):
                index = (dj[j] - 1) // 2
                Q = add(Q, P_pre[index])
            elif (dj[j] < 0):
                index = (-dj[j] - 1) // 2
                Q = add(Q, neg(P_pre[index]))
            
        return Q

    def Multiply_TimeTrials(N=300):
        import time
        r = getRandom(N)
        t0 = time.time()
        for i in range(0, len(r)):
            P = multiply_naive(G, r[i])
        t0 = time.time() - t0
        print("naive() => " + str(t0) + "s")

        t1 = time.time()
        for i in range(0, len(r)):
            P = multiply(G, r[i])
        t1 = time.time() - t1
        print("windowed_pre() => " + str(t1) + "s")
        print("% => " + str((t0-t1)*100/t1))

        Gi = hash_point_to_point(H)
        t2 = time.time()
        for i in range(0, len(r)):
            P = multiply(Gi, r[i])
        t2 = time.time() - t2
        print("windowed() => " + str(t2) + "s")
        print("% => " + str((t0-t2)*100/t2))
else:
    def multiply(P, s):
        return multiply_naive(P, s)

#shamir2 and shamir 3 are variations on multiply() using Shamir's Trick - Multiexponentiation
def find_msb(s):
    if (s == 0):
        return 0
    
    x = (1 << 255)
    while (s & x == 0):
        x = x >> 1

    return x

if (useShamir):
    def shamir(P, s):        
        b = len(P)
        assert(b == len(s))

        if (b == 1):
            return multiply(P[0], s[0])

        points = [NullPoint]*(2**b-1)

        bit = 1
        for i in range(0, b):
            for j in range(1, len(points)+1):
                if ((j & bit) > 0):
                    points[j-1] = add(points[j-1], P[i])

            bit = bit << 1

        x = find_msb(max(s))
        Pout = NullPoint

        while (x > 0):
            Pout = double(Pout)

            i = 0
            bit = 1
            for j in range(0, b):
                if ((x & s[j]) > 0):
                    i = i + bit

                bit = bit << 1

            if (i > 0):
                Pout = add(Pout, points[i-1])
                    
            x = x >> 1

        return Pout

    def shamir_batch(P, s, batch_size=6):
        if (batch_size == 0):
            return shamir(P, s)

        out = NullPoint
        
        #Use shamir in batches
        #Then do batch of remainder
        for i in range(0, len(s), batch_size):
            ip = i+batch_size
            if (ip > len(s)):
                ip = len(s)

            out = add(out, shamir(P[i:ip], s[i:ip]))

        return out

    def Shamir_TimeTrials(N=100, n=2):
        import time

        #Pick random Numbers
        r = []
        for i in range(0, N):
            r = r + [getRandom(n)]

        #Get generator points
        Gi = [G] + [NullPoint]*(n-1)
        for j in range(1, n):
                Gi[j] = hash_to_point(Gi[j-1])

        #Test naive method
        ms = time.time()
        for i in range(0, N):
            P = multiply(Gi[0], r[i][0])
            for j in range(1, n):
                P = add(P, multiply(Gi[j], r[i][j]))
                
        ms_end = time.time()
        t0 = ms_end-ms
        print("naive() => " + str(t0) + "s")

        #Test Shamir's trick
        ms = time.time()
        for i in range(0, N):
            P = shamir(Gi, r[i])
        ms_end = time.time()
        t1 = ms_end-ms
        print("shamir() => " + str(t1) + "s")
        print("% => " + str((t0-t1)*100/t0))
else:
    def shamir(P, s):
        if (len(P) == 1):
            return multiply(P[0], s[0])
        
        assert(len(P) == len(s))

        Pout = multiply(P[0], s[0])
        for i in range(1, len(P)):
            Pout = add(Pout, multiply(P[i], s[i]))
            
        return Pout

def sNeg(a):
    return (Ncurve - (a % Ncurve)) % Ncurve

def sAdd(a, b):
    return (a + b) % Ncurve

def sSub(a, b):
    return sAdd(a, sNeg(b))

def sMul(a, b):
    return (a * b) % Ncurve

def sSq(a):
    return sMul(a, a)

def sPow(a, p):
    out = a
    for i in range(1, p):
         out = sMul(out, a)
         
    return out

def sInv(a):
    a = a % Ncurve
    assert(a > 0)

    t1 = 0
    t2 = 1
    r1 = Ncurve
    r2 = a
    q = 0
    while (r2 != 0):
        q = r1 // r2
        (t1, t2, r1, r2) = (t2, t1 - q*t2, r2, r1 - q*r2)

    if (t1 < 0):
        t1 = t1 % Ncurve

    assert(sMul(a, t1) == 1)
    return t1

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
