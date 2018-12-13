pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

contract Structures {
	constructor() public {}
	
	struct G1Point {
	    uint x;
	    uint y;
	}
	
	struct RingSignature {
		//Inputs
		G1Point[] input_pub_keys;
		G1Point[] input_commitments;
		
		//Outputs
		G1Point[] output_pub_keys;
		G1Point[] output_commitments;
	
		//Signature Data
		uint c0;
		uint[] s;
		G1Point[] key_images;
	}
	
	struct BulletProof {
	    //Commitment(s)
		G1Point[] V;
		
		//Proof Data
		G1Point A;
		G1Point S;
		G1Point T1;
		G1Point T2;
		G1Point[] L;
		G1Point[] R;
		
		uint taux;
		uint mu;
		uint a;
		uint b;
		uint t;
		
		//Bits per commitment
		uint32 N;
	}
	
	function IsG1PointValid(G1Point memory point) public pure returns (bool) {
	    if (point.x == 0) return false;
	    if (point.y == 0) return false;
	    
	    //Passed
	    return true;
	}
	
	function IsG1PointOnCurve(G1Point memory point) public pure returns (bool) {
	    //(y^2 == x^3 + 3) % p
	    uint p = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;
	    uint left = mulmod(point.y, point.y, p);
	    uint right = addmod(mulmod(mulmod(point.x, point.x, p), point.x, p), 3, p);
	    
	    return (left == right);
	}
	
	function IsRingSignatureValid(RingSignature memory sig) public pure returns (bool) {
	    //Check inputs
	    uint input_length = sig.input_pub_keys.length;
	    if (input_length == 0) return false;
	    if (input_length != sig.input_commitments.length) return false;
	    
	    //Check Key Images, need at least 2 (1 for summation column)
	    uint m = sig.key_images.length;
	    if (m < 2) return false;
	    m -= 1;
	    if (input_length % m != 0) return false;
	    uint n = input_length / m;
	    
	    if ((m+1)*n != sig.s.length) return false;
	    
	    //Check outputs
	    uint output_length = sig.output_pub_keys.length;
	    if (output_length == 0) return false;
	    if (output_length != sig.output_commitments.length) return false;
	    
	    //Do boundary checks
	    if (n > 16) return false;
	    if (m > 4) return false;
	    if (output_length > 16) return false;
	    
	    //Passed
	    return true;
	}
	
	function IsBulletProofValid(BulletProof memory proof) public pure returns (bool) {
	    //Check proof
	    uint logMN = proof.L.length;
	    if (logMN == 0) return false;
	    if (logMN > 8) return false;
	    if (logMN != proof.R.length) return false;
	    
	    uint MN = (1 << logMN);
	    if (proof.N == 0) return false;
	    if (proof.N > 64) return false;
	    if (MN < proof.N) return false;
	    if (MN % proof.N != 0) return false;
	    uint M = MN / proof.N;
	    if (M != proof.V.length) return false;
	    
	    //Check for zeros
	    if (proof.taux == 0) return false;
	    if (proof.mu == 0) return false;
	    if (proof.a == 0) return false;
	    if (proof.b == 0) return false;
	    if (proof.t == 0) return false;
	    
	    //Passed
	    return true;
	}
}