# PlasmaCT
## What is it?
PlasmaCT is a combination of Confidential Transactions, Plasma, and Mimblewimble with various novel improvements.  The goal is to allow for private transactions on the Ethereum blockchain in a scalable way.
## Mimble Ideas
### Signatures
There are currently two types of signatures proposed.  The first are Schnorr signatures (R = r * G1, s) and the second are BLS signatures (S = x * HtP[msg], P = x * G1).  Both are used to prove that the remander (x * G1) is known for the difference between output and input pedersend commitments.
#### Schnorr
There are three benefits to using Schnorr signatures:
1. Public key recovery.  There is no need to supply the public key as it can be generated from R and s.
2. Faster per/tx verification.
3. Schnorr adaptor signatures (P, s, T).  These allow for "scriptless" scripts.  Execution of the script yeilds t for which T = t * G.  t is needed in order to validate the Schnorr signature.
#### BLS
There are 3 benefits to using BLS signatures:
1. Signature aggregation.  Multiple BLS signatures can be compacted down to one aggregate signature.  This is less data to keep track of on the child chain.
2. Kernel signature aggrigation (for CoinJoin).  Two or more mimble kernels can be combined to save space on the child-chain.  E.g. given kernels (S1, P1) for tx1 and (S2, P2) for tx2.  If tx1 and tx2 can be combined in mimble (one or more outputs of tx1 spent by tx2), the signature required for tx1+tx2 is (S1+S2, P1+P2).  In the Schnorr case, both kernels must be stored with the combined transation.
3. Non-interactive Mimblewimble.  Normally the receiver of a mimble tx must add an arbitrary remainder so that the sender cannot spend the new outputs.  The sender and receiver must be online to negotiate this.  Since we can aggregate BLS signatures, users can supply a BLS signature for their own public key (P = x * G1) on deposit.  When the sender wants to send the transaction, they simply calculate the remainder, create a BLS signature for this remainder, add the receivers public key to the output commitment, and then aggregate this signature with that of the receivers public key.  That way, a tx can be sent offline.  Later the pedersen commitment values and blinding factors must be communicated online prior to the receiver's spending.
## Plasma Ideas
### Deposit(BF : ecpoint, signature : bls/schnorr), value >= 1 szazbo
User sends a transaction to the RootChain contract with some amount of ETH, as well as an eliptic curve point BF, and a BLS or Schnorr signature proving that the sender knows bf such that BF = bf * G1.  A new utxo is created (v * H + bf * G1).

bf must be unknown to the chain since whoever knows bf would be authorized to spend the new UTXO.  Since the contract does not know bf, it must validate that BF = bf * G1.  If this signature is not provided, then alpha may be known by the user s.t. BF = alpha * H.  This would illicitly create coins.

### Send(inputs[] : ecpoint, outputs[] : ecpoint, bp : bulletproof, signature : bls/schnorr)
1. The block producer first verifies that all output commitments are commitments to positive values via the provided bp bulletproof.
2. The block producer then calculates the difference between the sum of all outputs and the sum of all inputs.  This should add up to a point P = p * G1, which is the same "public key" from the provided kernel signature.
3. If these are true, the outputs are converted to new UTXOs.  The inputs are now spent.  The transactions which created the inputs can now be combined with this new transaction (CoinJoin), either by storing the kernels together (Schnorr) or by aggregation (BLS).