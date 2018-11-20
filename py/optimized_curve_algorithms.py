from optimized_curve import *
from util import *

def mods(d, w):
    wPow = (1 << w)
    out = d % wPow
    if (out >= (wPow >> 1)):
        out = out - wPow

    return out

def NAF(d, w=5):
    di = []
    while (d > 0):
        if (d & 1) == 1:
            di = [mods(d, w)] + di
            d = d - di[0]
        else:
            di = [0] + di

        d = d >> 1

    return di

def EvaluateNAF(naf):
    d = 0
    for i in naf:
        d = (d << 1) + i

    return d

def NAF_Index(d, w=5):
    import math
    di = []
    while (d > 0):
        if (d & 1) == 1:
            d_mods = mods(d, w)
            d = d - d_mods
            
            if (d_mods > 0):
                di = [(d_mods + 1) >> 1] + di
            else:
                di = [-((-d_mods + 1) >> 1)] + di
        else:
            di = [0] + di

        d = d >> 1

    return di

def PrecomputePoints(P, w=5):
    assert(w > 1)
    points = [None]*(1 << (w-2))
    
    points[0] = P
    P2 = double(P)
    for i in range(1, len(points)):
        points[i] = add(points[i-1], P2)

    return points

def multiply(P, s, wBits=5):
    wPow = (1 << wBits)
    wPowOver2 = wPow // 2

    if (type(P[0]) == FQ):
        Q = NullPoint
        P_pre = PrecomputePoints(P, wBits)
    else:
        Q = NullPoint2
        P_pre = PrecomputePoints(P, wBits)

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

def multiexp(points, scalars, w=5):
    #Precompute points
    pp = [0]*len(points)
    for i in range(0, len(points)):
        pp[i] = PrecomputePoints(points[i], w)
    
    #Compute NAF form of each scalar
    scalars_naf = []
    max_naf_length = 0
    for d in scalars:
        scalars_naf += [NAF_Index(d, w)]
        naf_length = len(scalars_naf[-1])
        if naf_length > max_naf_length:
            max_naf_length = naf_length

    #Pad NAF's to be equal length
    scalars_naf_temp = scalars_naf
    scalars_naf = []
    for i in range(0, len(scalars_naf_temp)):
        naf_length_delta = max_naf_length - len(scalars_naf_temp[i])
        scalars_naf += [[0]*naf_length_delta + scalars_naf_temp[i]]
        
    #Compute multiplication
    Q = (FQ(0), FQ(0), FQ(0))
    for i in range(0, max_naf_length):
        Q = double(Q)

        for j in range(0, len(scalars_naf)):
            index = scalars_naf[j][i]

            if (index > 0):
                Q = add(Q, pp[j][index-1])
            elif (index < 0):
                Q = add(Q, neg(pp[j][-index-1]))

    return Q

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

#Elliptic Curve Multiplication
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

    Gi = hash_point_to_point1(H)
    t2 = time.time()
    for i in range(0, len(r)):
        P = multiply(Gi, r[i])
    t2 = time.time() - t2
    print("windowed() => " + str(t2) + "s")
    print("% => " + str((t0-t2)*100/t2))

#shamir2 and shamir 3 are variations on multiply() using Shamir's Trick - Multiexponentiation
def find_msb(s):
    if (s == 0):
        return 0
    
    x = (1 << 255)
    while (s & x == 0):
        x = x >> 1

    return x

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
        Gi[j] = hash_point_to_point1(Gi[j-1])

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

def test_multiexp(N=128, w=5):
    #Get random points and scalars
    import time
    t = time.time()
    points = []
    scalars = []
    for i in range(0, N):
        points += [multiply_naive(G, getRandom())]
        scalars += [getRandom()]

    t = time.time() - t
    print("setup done in " + str(t) + "s")

    #Test multiexp
    t = time.time()
    Q = multiexp(points, scalars, w)
    t = time.time() - t
    print("multiexp done in " + str(t) + "s")
    Qmultiexp = Q
    tmultiexp = t

    #Test naive algorithm
    t = time.time()
    Q = multiply_naive(points[0], scalars[0])
    for i in range(1, N):
        Q = add(Q, multiply_naive(points[i], scalars[i]))

    t = time.time() - t
    print("naive done in " + str(t) + "s")
    Qnaive = Q
    tnaive = t

    assert(eq(Qmultiexp, Qnaive))
    print("===")
    print("multiexp/naive = " + str(tmultiexp / tnaive * 100) + "%")
