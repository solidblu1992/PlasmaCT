from util import *

Gi = []
Hi = []
pvExpShamirSize = 3     #When using Shamir's trick, perform multi exponentiation in batches of 2*pvExpShamirSize

def GenBasePoints(N=128):
    Gi = [None]*N
    Hi = [None]*N

    for i in range(0, N):
        Gi[i] = hash_str_to_point("G" + str(i))
        Hi[i] = hash_str_to_point("H" + str(i))

    return (Gi, Hi)
	
def SerializeBasePoints():
	print("Gi:")
	for i in range(0, len(Gi)):
		print(point_to_str(Gi[i]) + ",")
	
	print()
	print("Hi:")
	for i in range(0, len(Hi)):
		print(point_to_str(Hi[i]) + ",")

def CheckBasePoints():
    for i in range(0, len(Gi)):
        if (is_on_curve(Gi[i], b)):
            print("Gi[" + str(i) + "] passes!")
        else:
            print("Gi[" + str(i) + "] fails!")

    for i in range(0, len(Hi)):
        if (is_on_curve(Hi[i], b)):
            print("Hi[" + str(i) + "] passes!")
        else:
            print("Hi[" + str(i) + "] fails!")		

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

if (useShamir):    
    def pvExpCustom(A, B, a, b):
        assert(len(a) == len(b))
        assert(len(A) >= len(a))
        assert(len(B) >= len(b))

        out = NullPoint

        #Use shamir in batches of 2*pvExpShamirSize points,
        #Then do batch of remainder
        for i in range(0, len(a), pvExpShamirSize):
            ip = i+pvExpShamirSize
            if (ip > len(a)):
                ip = len(a)
                
            out = add(out, shamir(A[i:ip] + B[i:ip], a[i:ip] + b[i:ip]))
    
        return out

    def pvExp(a, b):
        return pvExpCustom(Gi[:len(a)], Hi[:len(b)], a, b)
else:
    def pvExpCustom(A, B, a, b):
        assert(len(a) == len(b))
        assert(len(A) >= len(a))
        assert(len(B) >= len(b))

        out = NullPoint
        for i in range(0, len(a)):
            out = add(out, multiply(A[i], a[i]))
            out = add(out, multiply(B[i], b[i]))

        return out

    def pvExp(a, b):
        return pvExpCustom(Gi, Hi, a, b)

def pvAdd(A, B):
    assert(len(A) == len(B))

    out = [NullPoint]*len(A)
    for i in range(0, len(A)):
        out[i] = add(A[i], B[i])

    return out

def pvScale(A, s):
    out = [NullPoint]*len(A)
    for i in range(0, len(A)):
        out[i] = multiply(A[i], s)

    return out

def pvMul(A, a):
    assert(len(A) == len(a))

    out = [NullPoint]*len(A)
    for i in range(0, len(A)):
        out[i] = multiply(A[i], a[i])

    return out

#Generate Base Points
(Gi, Hi) = GenBasePoints()
