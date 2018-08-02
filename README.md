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
## Plasma Ideas
### Deposit(BF : ecpoint, signature : schnorr), value >= 1 szazbo
User sends a transaction to the RootChain contract with some amount of ETH, as well as an eliptic curve point BF, and a BLS or Schnorr signature proving that the sender knows bf such that BF = bf * G1.  A new utxo is created (v * H + bf * G1).

bf must be unknown to the chain since whoever knows bf would be authorized to spend the new UTXO.  Since the contract does not know bf, it must validate that BF = bf * G1.  If this signature is not provided, then alpha may be known by the user s.t. BF = alpha * H.  This would illicitly create coins.

### Send(inputs[] : ecpoint, outputs[] : ecpoint, bp : bulletproof, signature : bls/schnorr)
1. The block producer first verifies that all output commitments are commitments to positive values via the provided bp bulletproof.
2. The block producer then calculates the difference between the sum of all outputs and the sum of all inputs.  This should add up to a point P = p * G1, which is the same "public key" from the provided kernel signature.
3. If these are true, the outputs are converted to new UTXOs.  The inputs are now spent.  The transactions which created the inputs can now be combined with this new transaction (CoinJoin), either by storing the kernels together (Schnorr) or by aggregation (BLS).