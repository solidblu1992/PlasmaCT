from util import *
from bulletproof import *
from optimized_curve import *
from BLS import *


def GetRandomTxValues(input_count, output_count, max_value=1000):
    import random

    #Pick values
    v_in = [0]*input_count
    v_out = [0]*output_count
    total = 0

    for i in range(0, len(v_in)):
        v_in[i] = random.randint(0, max_value)
        total += v_in[i]

    for i in range(0, len(v_out) - 1):
        v_out[i] = random.randint(0, min([max_value, total]))
        total -= v_out[i]

    v_out[-1] = total

    #Pick blinding factors and offset
    bf_in = getRandom(input_count)
    bf_out = getRandom(output_count)
    
    if (input_count == 1):
        bf_in = [bf_in]

    if (output_count == 1):
        bf_out = [bf_out]

    #Calculate offset
    off_in = 0
    for i in range(0, len(v_in)):
        off_in = sAdd(off_in, hash_of_point(shamir([H, G], [v_in[i], bf_in[i]])))

    off_in = sMul(off_in, 2)

    off_out = 0
    for i in range(0, len(v_out)):
        off_out = sAdd(off_out, hash_of_point(shamir([H, G], [v_out[i], bf_out[i]])))
    off_out = sMul(off_out, 3)
    off = sAdd(off_out, off_in)

    #Calculate remainder
    rem = sSub(vSum(bf_out), sAdd(vSum(bf_in), off))
    
    return (v_in, v_out, bf_in, bf_out, off, rem)

class TxCommitment():
    def __init__(self, x, y):
        self.x = getRandom()
        self.y = getRandom()

class TxOutput():    
    blknum = 0
    commitment = 0
    bp = None

    def __init__(self, commitment, blknum=0, bp=None):
        self.blknum = blknum
        self.commitment = commitment
        self.bp = bp

    def Create(value, bf, createBP=False, blknum=0):
        if (isinstance(value, (list, tuple))):
            out = [None]*len(value)

            if (not isinstance(blknum, (list, tuple))):
                blknum = [blknum]*len(out)
            
            for i in range(0, len(out)):
                commitment = shamir([G, H], [bf[i], value[i]])
                
                if (createBP):
                    bp = BulletProof.Generate(value[i], power10=12, offset=0, gamma=bf[i], N=32, asset_addr=0)
                else:
                    bp = None
                    
                out[i] = TxOutput(commitment, blknum[i], bp)

            return out
        else:
            return TxOutput(shamir([G, H], [bf, value]), blknum)
    
class MimbleTx():
    def __init__(self, inputs, outputs, sig, offset=0):
        self.inputs = inputs
        self.outputs = outputs
        self.sig = sig
        self.offset = offset

    def verify(self):
        #Check for proper sig offset
        if (MimbleTx.get_expected_sig_offset(self.inputs, self.outputs) != self.offset):
            return False
        
        #Add up commitments
        commitment = NullPoint
        for i in range(0, len(self.inputs)):
            commitment = add(commitment, self.inputs[i].commitment)

        commitment = neg(commitment)

        for i in range(0, len(self.outputs)):
            commitment = add(commitment, self.outputs[i].commitment)

        #Verify BLS signature and verify that the public key balances the equality
        if (not self.sig.verify()):
            return False
        
        remainder = add(self.sig.P, multiply(G, self.offset))

        if (not eq(commitment, remainder)):
            return False

        return True

    def combine(tx1, tx2):
        #Naively combine tx's
        inp12 = tx1.inputs + tx2.inputs
        out12 = tx1.outputs + tx2.outputs
        sig12 = BLS.aggregate([tx1.sig, tx2.sig])
        off12 = sAdd(tx1.offset, tx2.offset)

        #Remove common inputs and outputs (cut-through)
        i = 0
        while i < len(inp12):
            j = 0
            while j < len(out12):
                if (eq(inp12[i].commitment, out12[j].commitment)):
                    #Adjust sig offset and BLS sig accordingly so that s = 2*sum(H(I))+3*sum(H(O)) to prevent reverse spends
                    off_diff = sMul(hash_of_point(inp12[i].commitment), 5)
                    off12 = sSub(off12, off_diff)
                    sig12 = BLS.aggregate([sig12, BLS.sign(off_diff)])
                    
                    inp12 = inp12[:i] + inp12[i+1:]
                    out12 = out12[:j] + out12[j+1:]
                    i -= 1
                    j -= 1

                j += 1
            i += 1

        #Return new Tx
        return MimbleTx(inp12, out12, sig12, off12)

    def get_expected_sig_offset(inputs, outputs):
        off_in = 0
        for i in range(0, len(inputs)):
            off_in = sAdd(off_in, hash_of_point(inputs[i].commitment))
        off_in = sMul(off_in, 2)

        off_out = 0
        for i in range(0, len(outputs)):
            off_out = sAdd(off_out, hash_of_point(outputs[i].commitment))
        off_out = sMul(off_out, 3)
        
        off = sAdd(off_out, off_in)
        return off

    def create_random(input_count, output_count, createBP=True, max_value=1000):
        import time
        (v_in, v_out, bf_in, bf_out, off, rem) = GetRandomTxValues(input_count, output_count, max_value=max_value)
        inputs1 = TxOutput.Create(v_in, bf_in)

        if (createBP):
            print("Creating " + str(output_count) + " bulletproofs...", end="")
            ms = time.time()
            
        outputs1 = TxOutput.Create(v_out, bf_out, createBP=createBP)

        if (createBP):
            t0 = time.time() - ms
            print("Done!")
            print("create() => " + str(t0) + "s (" + str(t0 / output_count) + "s per bulletproof)")
            
        sig1 = BLS.sign(rem)
        tx = MimbleTx(inputs1, outputs1, sig1, off)
        return tx

    def create_known(v_in, bf_in, v_out, bf_out, createBP=True):
        import time
        #Calculate remainder
        inputs1 = TxOutput.Create(v_in, bf_in)

        if (createBP):
            print("Creating " + str(len(bf_out)) + " bulletproofs...", end="")
            ms = time.time()
            
        outputs1 = TxOutput.Create(v_out, bf_out, createBP=createBP)

        off = MimbleTx.get_expected_sig_offset(inputs1, outputs1)
        rem = sSub(vSum(bf_out), sAdd(vSum(bf_in), off))

        if (createBP):
            t0 = time.time() - ms
            print("Done!")
            print("create() => " + str(t0) + "s (" + str(t0 / len(bf_out)) + "s per bulletproof)")
                  
        sig1 = BLS.sign(rem)
        tx = MimbleTx(inputs1, outputs1, sig1, off)
        return tx

    def print(self, detailed=False):
        print("Inputs: " + str(len(self.inputs)))
        if (detailed):
            for i in range(0, len(self.inputs)):
                print("\t" + str(i) + ": " + hex(CompressPoint(self.inputs[i].commitment)))
            
        print("Outputs: " + str(len(self.outputs)))
        if (detailed):
            for i in range(0, len(self.outputs)):
                print("\t" + str(i) + ": " + hex(CompressPoint(self.outputs[i].commitment)))
        
        print("Sig Offset: " + hex(self.offset))    
        print("Sig:")
        print("\tP: " + hex(CompressPoint(self.sig.P)))
        print("\tS: " + point_to_str(self.sig.S))

class MimbleBlock():
    def __init__(self, blknum=0):
        self.blknum = blknum
        self.diff_tx = None

    def add_tx(self, tx):
        if (self.diff_tx == None):
            self.diff_tx = tx
        else:
            self.diff_tx = self.diff_tx.combine(tx)

    def get_total_commitment(self):
        commitment = NullPoint

        if (self.diff_tx != None):
            for i in range(0, len(self.diff_tx.inputs)):
                commitment = add(commitment, self.diff_tx.inputs[i].commitment)

            commitment = neg(commitment)

            for i in range(0, len(self.diff_tx.outputs)):
                commitment = add(commitment, self.diff_tx.outputs[i].commitment)

        return commitment

    def get_total_signature(self):
        if (self.diff_tx != None):
            pub_key = self.diff_tx.sig.P
        else:
            pub_key = NullPoint

        return pub_key

    def get_bulletproofs(self):
        if (self.diff_tx != None):
            bp = []
            for i in range(0, len(self.diff_tx.outputs)):
                bp = bp + [self.diff_tx.outputs[i].bp]

            return bp
        else:
            return None

    def verify(self, verifyBP=True):
        import time

        t0, t1, t2 = 0, 0, 0
        if (self.diff_tx != None):
            ms = time.time()
            if (not self.diff_tx.verify()): return False
            t0 = time.time() - ms

            if (verifyBP):
                bp = self.get_bulletproofs()

                if (bp == None): return False
                if (len(bp) != len(self.diff_tx.outputs)): return False

                print("Verifying " + str(len(bp)) + " bulletproofs...", end="")
                ms = time.time()
                if (bp != None and not BulletProof.VerifyMulti(bp)): return False
                t1 = time.time() - ms
                t2 = t1 / len(bp)               
                print("Done!")
                
        print("verify() => " + str(t0+t1) + "s (" + str(t2) + "s per bulletproof)")
        return True
                
    def print(self):
        print("MimbleBlock:")
        print("Block Number: " + str(self.blknum))
        if (self.diff_tx != None):
            print("Total Commitment: " + hex(CompressPoint(self.get_total_commitment())))
            print("Diff Tx:")
            self.diff_tx.print()
        else:
            print("No Transactions")

#Quick Tx Test
if (True):
    #Tx 1
    tx1 = MimbleTx.create_random(3,2)
    tx2 = MimbleTx.create_known([7, 4], [25, 26], [11], [70])
    tx3 = MimbleTx.create_known([11], [70], [5, 6], [10, 21])
    x = MimbleBlock(5)
    x.add_tx(tx1)
    x.add_tx(tx2)
    x.add_tx(tx3)
    x.print()
