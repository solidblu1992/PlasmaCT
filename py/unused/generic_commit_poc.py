from util import *
from bulletproof import *
import random

#Generate 64 commitments
m = 32
assert(m % 2 == 0)
v0 = [0]*(m//2)
v1 = [1]*(m//2)
bf0 = getRandom(m//2)
bf1 = getRandom(m//2)

#Create Bulletproof(s)
batch_size=8

if (batch_size > m):
    batch_size = m
    
assert (m % batch_size == 0)
batches = m // batch_size
bp = [None]*(batches)

combined = list(zip(v0 + v1, bf0 + bf1))
random.shuffle(combined)
v_shuffle = []
bf_shuffle = []
v_shuffle[:], bf_shuffle[:] = zip(*combined)

for i in range(0, batches):
    bp[i] = BulletProof.Generate(v_shuffle[i*batch_size:(i+1)*batch_size], gamma=bf_shuffle[i*batch_size:(i+1)*batch_size], N=1)

    print("Bullet Proof " + str(i+1) + " of " + str(batches))
    bp[i].Print(detailed_commitment=False)

#Test Verification
if(BulletProof.VerifyMulti(bp)):
    print("Verification successful!")
else:
    print("Verification FAILED!")

#Build Commitment
def build_commit(v0, bf0, v1, bf1, v_desired=250, extra_bits=0):
    desired_bin = "0"*extra_bits + bin(v_desired)[2:]

    indices = list(range(0, len(v0)))
    min_len = min([len(v0), len(v1), len(bf0), len(bf1)])
    assert(len(desired_bin) <= min_len)
    random.shuffle(indices)

    C_total = NullPoint
    C = []
    bf_total = 0

    for i in range(0, len(desired_bin)):
        #Double Point
        C_total = double(C_total)
        bf_total = sMul(bf_total, 2)
        
        j = indices[i]
        if (int(desired_bin[i]) == 0):
            C = C + [shamir([G, H], [bf0[j], v0[j]])]
            bf = bf0[j]
        else:
            C = C + [shamir([G, H], [bf1[j], v1[j]])]
            bf = bf1[j]

        bf_total = sAdd(bf_total, bf)
        C_total = add(C_total, C[-1])            

    return (C_total, C, bf_total)

#Test Commitment
C_total, C, bf = build_commit(v0, bf0, v1, bf1, v_desired=250, extra_bits=5)
if eq(C_total, shamir([G, H], [bf, 250])):
    print("Commitment build successsful!")
else:
    print("Commitment build FAILED!")
