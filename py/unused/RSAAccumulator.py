from util import *

#RSA-2048
N = 0xc7970ceedcc3b0754490201a7aa613cd73911081c790f5f1a8726f463550bb5b7ff0db8e1ea1189ec72f93d1650011bd721aeeacc2acde32a04107f0648c2813a31f5b0b7765ff8b44b4b6ffc93384b646eb09c7cf5e8592d40ea33c80039f35b4f14a04b51f7bfd781be4d1673164ba8eb991c2c4d730bbbe35f592bdef524af7e8daefd26c66fc02c479af89d64d373f442709439de66ceb955f3ea37d5159f6135809f85334b5cb1813addc80cd05609f10ac6a95ad65872c909525bdad32bc729592642920f24c61dc5b3c3b7923e56b16a4d9d373d8721f24a3fc0f1b3131f55615172866bccc30f95054c824e733a5eb6817f7bc16399d48c6361cc7e5
g = 0x1999

def CheckIfProbablyPrime(x):
    if (x == 1):
        return False
    
    if (x <= 3):
        return True
    
    return pow(2, x - 1, x) == 1

def acc(v=1, A=g):
    #Trivial or first case
    if (v == 1):
        return A

    #Should only accumulate prime numbers
    assert(CheckIfProbablyPrime(v))
    
    Aprime = pow(A, v, N)
    return Aprime

def prove(v, A, acc_values):
    x = 1
    for _ in acc_values:
        if _ != v:
            x = x * _ % N

    assert(pow(pow(g, x, N), v, N) % N == A)
    return x

#Start accumulator
A = acc()

acc_values = [2, 3, 5, 7, 11, 13, 31]

for _ in acc_values:
    A = acc(_, A)
