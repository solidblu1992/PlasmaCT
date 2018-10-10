from optimized_curve import *

def GetRandom():
    import random
    return random.getrandbits(256)

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

def test_multiexp(N=128, w=5):
    #Get random points and scalars
    import time
    t = time.time()
    points = []
    scalars = []
    for i in range(0, N):
        points += [multiply_naive(G, GetRandom())]
        scalars += [GetRandom()]

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
