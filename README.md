# PlasmaCT
## What is it?
PlasmaCT is a combination of Confidential Transactions, Plasma, and Mimblewimble with various novel improvements.  The goal is to allow for private transactions on the Ethereum blockchain in a scalable way.
## Mimble Ideas
### Signatures
There are currently two types of signatures proposed.  The first are Schnorr signatures (R = r * G1, s) and the second are BLS signatures (S = x * HtP[msg], P = x * G1).  Both are used to prove that the remander (x * G1) is known for the difference between output and input pedersen commitments.
#### Schnorr.sign(msg, x) -> (R : G1Point, s : uint)
(+) Smaller signatures per/tx.

(+) Faster per/tx verification.

(+) Schnorr adaptor signatures (P, s, T).  These allow for "scriptless" scripts.  Correct execution of the script yeilds t for which T = t * G.  t is needed in order to validate the Schnorr signature: (P, s) = invalid, (P, s+t) = valid.

(-) Can't aggregate signatures, always have a growing number of tx "kernels".

#### BLS.sign(msg, x) -> (P : G1Point, S : G2Point)
(+) Better signature aggregation.  If the signatures all sign the same message then all signatures can be aggregated into one.  Special attention needs to be given to the fact that if sign(msg, -x) can be calculated from sign(msg, x) without knowing x.

(-) Slower per/tx verfification by an order of magnitude

(-) No scriptless script support.

## On Chain
### Deposit(BF : G1Point, signature : schnorr), value >= 1 szazbo
User sends a transaction to the RootChain contract with some amount of ETH, as well as an eliptic curve G1 point BF, and a BLS or Schnorr signature proving that the sender knows bf such that BF = bf * G1.  A new utxo is created (v * H + bf * G1).

bf must be unknown to the chain since whoever knows bf would be authorized to spend the new UTXO.  Since the contract does not know bf, it must validate that BF = bf * G1.  If this signature is not provided, then alpha may be known by the user s.t. BF = bf * G1 + alpha * H.  This would illicitly create coins.

### PublishBlock(bytes32 block_hash)
The block producer publishes the current block hash to the main chain.  The block format would look something like the following.  Note that all tx's included in the block are aggregated using the same techniques as MimbleWimble.


Prameter | Type | Description
--- | --- | ---
blk_num | uint | Number of the block
sig(0) | BLS | Aggregated signature for the total block tx, signing block number = 0.  Possibly used in future for aggregating historical blocks.
sig(blk_num) | BLS | Aggregated signature for the total block tx, signing current block number
sig_offset | uint | Total signature offset for the total block tx.  Used to obscure groupings of inputs and outputs.
outputs | {uint, BulletProof}[] | All outputs included in the total block tx.  uint specifies current block number.  BulletProof contains output commitment
inputs | {uint, G1Point}[] | All inputs included in the total block tx.  uint specifies the block number that created the input.

## Off Chain
### Send(inputs : G1Point[], outputs : G1Point[], bp : bulletproof[], signature : bls/schnorr, signature_offset : uint)
1. The block producer first verifies that all output commitments are commitments to positive values via the provided bp bulletproofs.
2. The block producer then calculates the difference between the sum of all outputs and the sum of all inputs.  This should add up to a point P = recover(signature) + signature_offset * G1.
3. If using BLS signatures, the given signature must sign the new block number to prevent transaction reversal.  This means that only transactions included in the same block can be aggregated.  In the future, it may be possible to provide two signatures: BLS.sign(block number, x) and BLS.sign(0, x).  For a valid tx, both must have the same public key.  How the full block history aggregation would work in a Plasma context is not yet clear, however.  Need to think up a sufficient exit game which can withstand data availability.  
4. If these are true, the outputs will be converted to new UTXOs and the inputs spent.  The transactions which created the inputs can now be combined with this new transaction (CoinJoin), either by storing the kernels together (Schnorr) or by aggregation (BLS) and adding the signature_offsets together.
