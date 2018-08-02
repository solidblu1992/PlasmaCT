from util import *

Gi = []
Hi = []
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

if (useShamir):    
    def pvExpCustom(A, B, a, b):
        assert(len(a) == len(b))
        assert(len(A) >= len(a))
        assert(len(B) >= len(b))

        return shamir_batch(A+B, a+b)

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
