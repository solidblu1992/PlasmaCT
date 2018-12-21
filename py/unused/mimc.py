from util import *

k = getRandom(64)

def mimc(inp, steps, round_constants, forward=True):
    if (type(inp) != FQ):
        inp = FQ(inp)

    if (forward):
        power = 3
    else:
        power = (2*Pcurve-1) // 3

    import time
    start = time.time()
    for i in range(0, steps-1):
        inp = inp**power + round_constants[i % len(round_constants)]
    delta = time.time() - start
    print("MIMC computed in %.4f sec" % delta)
    return inp
