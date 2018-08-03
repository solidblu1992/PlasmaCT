#A bunch of work to find the cofactor for Fp2
def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

#See Barreto and Naehrig, Pairing-Friendly Elliptic Curves of Prime Order
#https://eprint.iacr.org/2005/133.pdf
bn128_x = 4965661367192848881 #sqrt((Pcurve-Ncurve)//6)
bn128_t = 6*(bn128_x**2)+1
bn128_n = 36*(bn128_x**4)+36*(bn128_x**3)+18*(bn128_x**2)+6*(bn128_x)+1
bn128_p = 36*(bn128_x**4)+36*(bn128_x**3)+24*(bn128_x**2)+6*(bn128_x)+1

#Number of points #E_Fpm
def EFpm(m, p=bn128_p, t=bn128_t):
    tau = [0]*(m+1)
    tau[0] = 2
    tau[1] = t
    for i in range(1, m):
        tau[i+1] = t*tau[i]-p*tau[i-1]

    q = p**m
    return (q + 1 - tau[m])

assert(EFpm(1) == bn128_n)

#Number of points #E'_Fp(k/6)=#E'_Fp2 (k=12, sextic twist)
#See Scott et all, Fast hashing to G2 on pairing friendly curves
#https://eprint.iacr.org/2008/530.pdf
def EpFp2():
    m = 2
    p = bn128_p
    t = bn128_t
    tau = [0]*(m+1)
    tau[0] = 2
    tau[1] = t
    for i in range(1, m):
        tau[i+1] = t*tau[i]-p*tau[i-1]

    q = p**m
    f = isqrt((4*q-tau[m]**2) // 3)
    
    return (q + 1 - (3*f + tau[m]) // 2)


Fp2_cofactor = EpFp2() // bn128_n
