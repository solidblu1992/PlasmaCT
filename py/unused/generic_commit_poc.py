from util import *
from bulletproof import *
import random

#Generate 64 commitments
m = 64
v = [0]*(m//2) + [1]*(m//2)
bf = getRandom(m)

#Create Bulletproof(s)
batch_size=8

if (batch_size > m):
    batch_size = m
    
assert (m % batch_size == 0)
batches = m // batch_size
bp = [None]*(batches)

combined = list(zip(v, bf))
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

