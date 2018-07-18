from util import *
from optimized_pairing import *

xk = getRandom()
P = multiply(G1, xk)

M = multiply(G2, getRandom())
S = multiply(M, xk)

a = pairing(S, G1)
b = pairing(M, P)
