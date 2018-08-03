from util import *
from bulletproof import *
from optimized_curve import *
from Schnorr import *
import rlp
from rlp.sedes import CountableList, big_endian_int


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
    off = getRandom()

    #Calculate remainder
    rem = sSub(vSum(bf_out), sAdd(vSum(bf_in), off))
    
    return (v_in, v_out, bf_in, bf_out, off, rem)

class TxCommitment(rlp.Serializable):
    fields = [
        ('x', big_endian_int),
        ('y', big_endian_int)
    ]

    def __init__(self, x, y):
        self.x = getRandom()
        self.y = getRandom()

class TxOutput(rlp.Serializable):

    fields = [
        ('commitment', TxCommitment)
    ]
    
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
    
class MimbleTx(rlp.Serializable):

    fields = [
        ('inputs', CountableList(TxOutput)),
        ('outputs', CountableList(TxOutput)),
        ('sig', CountableList(Schnorr)),
        ('offset', big_endian_int)
    ]

    def __init__(self, inputs, outputs, sigs, offset=0):
        self.inputs = inputs
        self.outputs = outputs
        self.sigs = sigs
        self.offset = offset

    def verify(self):
        #Add up commitments
        commitment = NullPoint
        for i in range(0, len(self.inputs)):
            commitment = add(commitment, self.inputs[i].commitment)

        commitment = neg(commitment)

        for i in range(0, len(self.outputs)):
            commitment = add(commitment, self.outputs[i].commitment)

        #Add up Schnorr public keys, see if remainder is signed (x known s.t. remainder = x*)
        remainder = add(Schnorr.recover_multiple(self.sigs), multiply(G, self.offset))

        if (not eq(commitment, remainder)):
            return False

        return True

    def combine(tx1, tx2):
        #Naively combine tx's
        inp12 = tx1.inputs + tx2.inputs
        out12 = tx1.outputs + tx2.outputs
        sigs12 = tx1.sigs + tx2.sigs
        off12 = sAdd(tx1.offset, tx2.offset)

        #Remove common inputs and outputs (cut-through)
        i = 0
        while i < len(inp12):
            j = 0
            while j < len(out12):
                if (eq(inp12[i].commitment, out12[j].commitment)):
                    inp12 = inp12[:i] + inp12[i+1:]
                    out12 = out12[:j] + out12[j+1:]
                    i -= 1
                    j -= 1

                j += 1
            i += 1

        #Return new Tx
        return MimbleTx(inp12, out12, sigs12, off12)

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
            
        sigs1 = [Schnorr.sign(rem)]
        tx = MimbleTx(inputs1, outputs1, sigs1, off)
        return tx
    
    def create_known(v_in, bf_in, v_out, bf_out, createBP=True):
        import time
        #Calculate remainder
        inputs1 = TxOutput.Create(v_in, bf_in)

        if (createBP):
            print("Creating " + str(len(bf_out)) + " bulletproofs...", end="")
            ms = time.time()
            
        outputs1 = TxOutput.Create(v_out, bf_out, createBP=createBP)

        off = getRandom()
        rem = sSub(vSum(bf_out), sAdd(vSum(bf_in), off))

        if (createBP):
            t0 = time.time() - ms
            print("Done!")
            print("create() => " + str(t0) + "s (" + str(t0 / len(bf_out)) + "s per bulletproof)")
                  
        sig1 = [Schnorr.sign(rem)]
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
            
        print("Sigs: " + str(len(self.sigs)))
        if (detailed):
            for i in range(0, len(self.sigs)):
                print("Sig " + str(i) + ":")
                print("\tR: "+ hex(CompressPoint(self.sigs[i].R)))
                print("\ts: "+ hex(CompressPoint(self.sigs[i].s)))
                
        print("Sig Offset: " + hex(self.offset))

class MimbleBlock(rlp.Serializable):
    blknum = 0
    diff_tx = None

    fields = [
        ('transaction_set', CountableList(MimbleTx)),
    ]

    def __init__(self, blknum=0):
        self.blknum = blknum

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
            pub_key = Schnorr.recover_multiple(self.diff_tx.sigs)
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
            print("Multisignature: " + hex(CompressPoint(self.get_total_signature())))
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
