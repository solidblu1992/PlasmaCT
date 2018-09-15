from util import *
import random
import math
from optimized_curve import *

def mod_inv(a, p):
    a = a % p
    assert(a > 0)

    t1 = 0
    t2 = 1
    r1 = p
    r2 = a
    q = 0
    while (r2 != 0):
        q = r1 // r2
        (t1, t2, r1, r2) = (t2, t1 - q*t2, r2, r1 - q*r2)

    if (t1 < 0):
        t1 = t1 % p

    assert((a * t1) % p == 1)
    return t1

p_256   = 0xb03855fd279525daabb25500360896830947bab4a63904806bd4760ea3be2a05
p_318   = 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab
p_512   = 0x8a5cf0c6ca8da45c8a73f36d401a36bf0c0d9ef22552843e6ab444d3d25dc1f3c6b23cf48897ad25fcbe762ebc11bc00eb0a64a5c7a95b3653f44bea5ae7cf59
p_1024a = 0xbc90e060fc8c6286d0cd30ea57ee95dbe6650efdb628de03cde653d91c54975103d429017091e7174729f944b4ed580484341af2246e9c5bb339c82d28cbb6707d6be4b7fa3c431aeba0b8136daa99460bcf33f567dc7ee2471c061899cc0d9ad4bfae1f3ec29f642134aa91f92b8322ae16e05abce22cf63605f0caff40250d
p_1024b = 0xbf6c55c2af0568377a8a188823ec5d433e540780637a7f8b54098a447fd2ef0b44bd2ba77aff26f49cc5ddfd7507474a341c540379523aa99d28990101ee44e637b4dbc0f90f57b231cf1ba50b2c79db58e4a15b2d15fcb1c7bf674c69ca201bed09c117121784c59c2150c52fa4a18e4daf7f1e9fb7d202058d0f3a9eff5169
p = p_1024a

N = 32
bits = math.ceil(math.log(p,2))
constants = [(random.getrandbits(bits) % p) for i in range(0, N)]

def mimc(x, steps=1000):
    import time
    t = time.time_ns()

    for i in range(0, steps):
        x = (pow(x, 3, p) + constants[i % N]) % p

    t = time.time_ns() - t
    print("forward mimc complete in " + str(t / 1000000000) + " s")
    return (x, t)

def inv_mimc(x, steps=1000):
    import time
    t = time.time_ns()

    end = (steps-1) % N
    power = ((2*p-1)*mod_inv(3, p)) % p
    for i in range(0, steps):
        x = pow((x - constants[(end-i) % N]) % p, power, p)

    t = time.time_ns() - t
    print("reverse mimc complete in " + str(t / 1000000000) + " s")
    return (x, t)

def test_mimc_fwd_rev(target_s = 24*60*60, steps_test = 1000):
    x = random.getrandbits(bits) % p
    print("Testing mimc...")
    (y, t1) = mimc(x, 1000)
    (xp, t2) = inv_mimc(y, 1000)
    print("rev/fwd = " + str(t2/t1))

    target_ns = target_s*1000000000
    steps = math.ceil((target_ns/t2)*steps_test)
    print("steps to acheive target = " + str(steps))
    print("estimated generation time = " + str(t1 * steps / steps_test / 60000000000) + " min")
    return steps

def get_delayed_commitment():
    #3 min delay
    print()
    steps = test_mimc_fwd_rev(3*60)
    t = random.getrandbits(bits) % p
    (tp, dummy) = mimc(t, steps)
    T = multiply(G, t)
    return (t, tp, T, steps)

def test_delayed_commitment(tp, T, steps):
    print()
    print("testing delayed commitment...")
    (t, delta_time) = inv_mimc(tp, steps)
    if (not eq(multiply(G, t), T)): return False
    print("done!")
    return (t, delta_time)



(t, tp, T, steps) = get_delayed_commitment()
test_delayed_commitment(tp, T, steps)
