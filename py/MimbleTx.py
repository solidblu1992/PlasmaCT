from util import *
from sha3 import *
from optimized_curve import *
from Schnorr import *

class TxOutput:
    blknum = 0
    commitment = 0

    def __init__(self, commitment, blknum=0):
        self.blknum = blknum
        self.commitment = commitment

    def Create(value, bf, blknum=0):
        if (isinstance(value, (list, tuple))):
            out = [None]*len(value)

            if (not isinstance(blknum, (list, tuple))):
                blknum = [blknum]*len(out)
            
            for i in range(0, len(out)):
                out[i] = TxOutput(shamir([G1, H], [bf[i], value[i]]), blknum[i])

            return out
        else:
            return TxOutput(shamir([G1, H], [bf, value]), blknum)
    
class MimbleTx:
    blknum = 0
    inputs = None
    outputs = None
    sigs = None

    def __init__(self, inputs, outputs, sigs, blknum=0):
        self.inputs = inputs
        self.outputs = outputs
        self.sigs = sigs
        self.blknum = blknum

    def verify(self):
        #Add up commitments
        commitment = NullPoint
        for i in range(0, len(self.inputs)):
            commitment = add(commitment, self.inputs[i].commitment)

        commitment = neg(commitment)

        for i in range(0, len(self.outputs)):
            commitment = add(commitment, self.outputs[i].commitment)

        #Add up Schnorr public keys, see if remainder is signed (x known s.t. remainder = x*G1)
        remainder = NullPoint
        for sig in self.sigs:
            #Verify Signature, is this necessary?
            if(not sig.verify()):
                return False
            
            remainder = add(remainder, sig.recover())

        if (not eq(commitment, remainder)):
            return False

        return True

    def combine(tx1, tx2):
        #Naively combine tx's
        inp12 = tx1.inputs + tx2.inputs
        out12 = tx1.outputs + tx2.outputs
        sigs12 = tx1.sigs + tx2.sigs
        blknum = max([tx1.blknum, tx2.blknum])

        #Remove common inputs and outputs (cut-through)
        i = 0
        while i < len(inp12):
            j = 0
            while j < len(out12):       
                print("i:" + str(i) + ", j:" + str(j))
                print("i:" + str(len(inp12)) + ", j:" + str(len(out12)))
                if (eq(inp12[i].commitment, out12[j].commitment)):
                    inp12 = inp12[:i] + inp12[i+1:]
                    out12 = out12[:j] + out12[j+1:]
                    i -= 1
                    j -= 1

                j += 1
            i += 1

        #Return new Tx
        return MimbleTx(inp12, out12, sigs12, blknum)

    def print(self):
        print("MimbleTx:")
        print("Inputs: " + str(len(self.inputs)))
        print("Outputs: " + str(len(self.outputs)))
        print("Sigs: " + str(len(self.sigs)))

#Quick Tx Test
if (True):
    inputs1 = TxOutput.Create([10, 5, 7], [25, 30, 40])
    outputs1 = TxOutput.Create([13, 9], [5, 95])
    sigs1 = [Schnorr.sign(5)]

    tx1 = MimbleTx(inputs1, outputs1, sigs1, 1)
    tx1.verify()

    inputs2 = TxOutput.Create([13, 9], [5, 95])
    outputs2 = TxOutput.Create([19, 3], [101, 213])
    sigs2 = [Schnorr.sign(214)]

    tx2 = MimbleTx(inputs2, outputs2, sigs2, 2)
    tx2.verify()

    tx12 = MimbleTx.combine(tx1, tx2)
