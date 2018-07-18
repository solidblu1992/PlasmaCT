from __future__ import absolute_import

from optimized_secp256k1_elements import (
    field_modulus,
    FQ,
)

curve_order = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Curve is y**2 = x**3 + 7
b = FQ(7)

# Generator for curve over FQ
G = (FQ(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798), FQ(0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8), FQ(1))

# Check if a point is the point at infinity
def is_inf(pt):
    return pt[-1] == pt[-1].__class__.zero()


# Check that a point is on the curve defined by y**2 == x**3 + b
def is_on_curve(pt, b):
    if is_inf(pt):
        return True
    x, y, z = pt
    return y**2 * z - x**3 == b * z**3

assert is_on_curve(G, b)

# Elliptic curve doubling
def double(pt):
    x, y, z = pt
    W = 3 * x * x
    S = y * z
    B = x * y * S
    H = W * W - 8 * B
    S_squared = S * S
    newx = 2 * H * S
    newy = W * (4 * B - H) - 8 * y * y * S_squared
    newz = 8 * S * S_squared
    return newx, newy, newz

# Elliptic curve addition
def add(p1, p2):
    one, zero = p1[0].__class__.one(), p1[0].__class__.zero()
    if p1[2] == zero or p2[2] == zero:
        return p1 if p2[2] == zero else p2
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    U1 = y2 * z1
    U2 = y1 * z2
    V1 = x2 * z1
    V2 = x1 * z2
    if V1 == V2 and U1 == U2:
        return double(p1)
    elif V1 == V2:
        return (one, one, zero)
    U = U1 - U2
    V = V1 - V2
    V_squared = V * V
    V_squared_times_V2 = V_squared * V2
    V_cubed = V * V_squared
    W = z1 * z2
    A = U * U * W - V_cubed - 2 * V_squared_times_V2
    newx = V * A
    newy = U * (V_squared_times_V2 - A) - V_cubed * U2
    newz = V_cubed * W
    return (newx, newy, newz)

# Elliptic curve point multiplication
def multiply_naive(pt, n):
    if n == 0:
        return (pt[0].__class__.one(), pt[0].__class__.one(), pt[0].__class__.zero())
    elif n == 1:
        return pt
    elif not n % 2:
        return multiply_naive(double(pt), n // 2)
    else:
        return add(multiply_naive(double(pt), int(n // 2)), pt)

def eq(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return x1 * z2 == x2 * z1 and y1 * z2 == y2 * z1

def normalize(pt):
    x, y, z = pt
    return (x / z, y / z)

# Convert P => -P
def neg(pt):
    if pt is None:
        return None
    x, y, z = pt
    return (x, -y, z)
