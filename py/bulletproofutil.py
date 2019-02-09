from util import *
from optimized_curve_algorithms import *

Gi = []
Hi = []
GiHiTree = None

def GenBasePoints(N=64):
    Gi = [None]*N
    Hi = [None]*N

    for i in range(0, N):
        hasher = sha3.keccak_256(bytes("Gi", "utf"))
        hasher.update(int_to_bytes(i))
        Gi[i] = point1_from_t(bytes_to_int(hasher.digest()))

        hasher = sha3.keccak_256(bytes("Hi", "utf"))
        hasher.update(int_to_bytes(i))
        Hi[i] = point1_from_t(bytes_to_int(hasher.digest()))

    return (Gi, Hi)

def GenBasePointsMerkel(chunk_size=16):
    assert(len(Gi) % chunk_size == 0)
    assert(len(Hi) % chunk_size == 0)

    #Assemble Level 0
    #print("Merkel Tree:")
    #print("Level 0")
    
    tree = []
    chunks = [None] * (len(Gi) // chunk_size)
    for i in range(0, len(chunks)):
        chunks[i] = hash_of_base_points(chunk_size, i*chunk_size)
        #print(bytes_to_str(chunks[i]))

    tree += [chunks]

    #Merkelize chunks
    level=1
    while True:
        #print()
        #print("Level " + str(level))
        new_chunks = [None] * (len(chunks) // 2)
        for i in range(0, len(new_chunks)):
            new_chunks[i] = hash_of_bytes(chunks[2*i] + chunks[2*i+1])
            #print(bytes_to_str(new_chunks[i]))

        tree += [new_chunks]
            
        if (len(new_chunks) == 1):
            return tree
        else:
            level += 1
            chunks = new_chunks

def BasePointsToBytes(count=16, start=0):
    assert(len(Gi) >= (start+count))
    assert(len(Hi) >= (start+count))

    b = b""
    for i in range(start, start+count):
        b += int_to_bytes(Gi[i][0].n)
        b += int_to_bytes(Gi[i][1].n)
        b += int_to_bytes(Hi[i][0].n)
        b += int_to_bytes(Hi[i][1].n)

    return b

def hash_of_base_points(count=16, start=0):
    b = BasePointsToBytes(count, start)
    hasher = sha3.keccak_256(b)
    return hasher.digest()

def merkel_chunk_proof(chunk_number):
    tree = GiHiTree
    proof = [tree[0][chunk_number]]
    for i in range(0, len(tree)-1):
        hash_order = (chunk_number & 1)

        if (hash_order == 0):
            next_hash = tree[i][chunk_number + 1]
        else:
            next_hash = tree[i][chunk_number - 1]

        proof += [(hash_order, next_hash)]
        chunk_number // 2

    proof += tree[-1]

    return proof

def check_merkel_proof(proof):
    assert(len(proof) > 2)

    leaf_hash = proof[0]
    print(bytes_to_str(leaf_hash))
    for i in range(1, len(proof)-1):
        assert(type(proof[i]) == tuple)

        #Even Leaf
        if (proof[i][0] == 0):
            leaf_hash = hash_of_bytes(leaf_hash + proof[i][1])
        #Odd Leaf
        else:
            leaf_hash = hash_of_bytes(proof[i][1] + leaf_hash)            
        
    return (leaf_hash == proof[-1])
        
def PrintBasePoints_ETH(count=16, start=0):
    print(bytes_to_str(BasePointsToBytes(count, start)))

def PrintHashOfBasePoints(count=16, start=0):
    print(bytes_to_str(hash_of_base_points(count,start)))

def PrintBasePointMerkelTree():
    print("Merkel Tree:")
    for i in range(0, len(GiHiTree)):
        print()
        print("Level " + str(len(GiHiTree)-i-1) + ":")

        for j in range(0, len(GiHiTree[i])):
            print(bytes_to_str(GiHiTree[i][j]))

def PrintChunk_ETH(chunk_number):
    chunk_size = len(Gi) // (1 << (len(GiHiTree)-1))
    PrintBasePoints_ETH(chunk_size, chunk_number*chunk_size)

def PrintChunkProof_ETH(chunk_number):
    proof = merkel_chunk_proof(chunk_number)

    levels = len(proof)-2
    
    print("chunk_index")
    print(chunk_number)

    for i in range(0, levels):
        print()
        print("level_" + str(levels-i) + "_hash")
        print(bytes_to_str(proof[i+1][1]))
    
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
   
def pvExpCustom(A, B, a, b):
    assert(len(a) == len(b))
    assert(len(A) >= len(a))
    assert(len(B) >= len(b))

    #return shamir_batch(A+B, a+b)
    return multiexp(A+B, a+b)

def pvExp(a, b):
    #return pvExpCustom(Gi[:len(a)], Hi[:len(b)], a, b)
    return multiexp(Gi[:len(a)]+Hi[:len(b)], a+b)

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
GiHiTree = GenBasePointsMerkel(16)

if (True):
    chunk_num = 0
    
    print("leaf_bytes:")
    PrintChunk_ETH(chunk_num)

    print()
    PrintChunkProof_ETH(chunk_num)
