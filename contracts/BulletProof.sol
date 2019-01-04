pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";
import "./Scalar.sol";
import "./Vector.sol";

library BulletProof {
    using G1Point for G1Point.Data;
    
    struct Data {	    
		//Comitments
		G1Point.Data[] V;
		
		//Signature Data
		G1Point.Data A;
		G1Point.Data S;
		G1Point.Data T1;
		G1Point.Data T2;
		G1Point.Data[] L;
		G1Point.Data[] R;
		uint taux;
		uint mu;
		uint a;
		uint b;
		uint t;
		uint N;
		address asset_addr;
	}
	
	function GetAssetH(address asset_addr) public view returns (G1Point.Data memory) {
		//Get H point for asset
		if (asset_addr == address(0)) {
			//ETH
			return G1Point.GetH();
		}
		else {
		    //e.g.  DAI = 0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359
		    //      MKR = 0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2
		    //H(DAI)    = 0x03085dd220a21810f928772272815e0fb2e6d20544d31a448c6316c17cc2aa951d
		    //H(MKR)    = 0x03220271980c442123248f74b3f06f980cf58503dfe7b5d37b8f1ed9537eaaa75b
			return G1Point.HashAddressToPoint(asset_addr);
		}
	}
	
	struct BPMemory {
	    //Implicit Signature Parameters
	    uint MN;
	    
	    //Fiat-Shamir
	    uint y;
	    uint z;
	    uint x;
	    uint x_ip;
	    
	    //Vectors
	    uint[] vp2;
	    uint[] vpy;
	    uint[] vpyi;
	    
	    //Other terms
	    uint k;
	    uint[] w;
	    uint[] w_inv;
	    uint gScalar;
	    uint hScalar;
	    uint[] gScalars;
	    uint[] hScalars;
	    
	    //Elliptic Curve Points and Parameters
	    G1Point.Data H;
	    
	    //General purpose uint
	    uint temp;
	    uint temp2;
	    uint[] temp_vec;
	}
		
	function IsValid(Data memory proof) public view returns (bool) {
	    //Group memory variables together to reduce stack depth
	    BPMemory memory mem;
	    uint i;
	    uint j;
	    uint modulo;
	    
		//Check inputs
	    if (proof.V.length == 0) return false;
		
		mem.temp = proof.L.length; //logMN
		if (mem.temp == 0) return false;
		if (proof.R.length != mem.temp) return false;
		mem.MN = (1 << mem.temp);
		
		if (proof.N == 0) return false;
		if (proof.N > 64) return false;
		if ((proof.N * proof.V.length) != mem.MN) return false;
	    
		//Get H point for asset
		mem.H = GetAssetH(proof.asset_addr);
		
		///Calculate Fiat-Shamir
		//y = hash(V[], A, S)
		//z = hash(y)
		//x = hash(z, T1, T2)
		//x_ip = hash(x, taux, mu, t)
		
		//temp2 = serialize(V[])
		mem.temp_vec = new uint[](proof.V.length*2);
		j = 0;
		for (i = 0; i < proof.V.length; i++) {
		    mem.temp_vec[j] = proof.V[i].x;
		    mem.temp_vec[j+1] = proof.V[i].y;
		    j += 2;
		}
		
		mem.y = uint(keccak256(abi.encodePacked(mem.temp_vec, proof.A.x, proof.A.y, proof.S.x, proof.S.y)));
		mem.z = uint(keccak256(abi.encodePacked(mem.y)));
		mem.x = uint(keccak256(abi.encodePacked(mem.z, proof.T1.x, proof.T1.y, proof.T2.x, proof.T2.y)));
		mem.x_ip = uint(keccak256(abi.encodePacked(mem.x, proof.taux, proof.mu, proof.t)));
		
		///Calculate vectors
		//vp2 = 2^0, 2^1, 2^2, ..., 2^(N-1)
		//vpy = y^0, y^1, y^2, ..., y^(MN-1)
		//vpyi = y^0, y^-1, y^-2, ..., y^(1-MN)
		mem.vp2 = Vector.Powers(2, proof.N);
		mem.vpy = Vector.Powers(mem.y, mem.MN);
		mem.vpyi = Vector.Powers(Scalar.Inverse(mem.y), mem.MN);
		
		///Calculate k
		//k = -[z^2 * sum(vpy)] - sum[z^{j+2} * sum(vp2)]
		modulo = G1Point.GetN();
		
		mem.temp = mulmod(mem.z, mem.z, modulo); //temp = z^2
		mem.temp2 = (1 << mem.vp2.length) - 1; //sum(vp2)
		mem.k = mulmod(mem.k, Vector.Sum(mem.vpy), modulo);
		
		for (i = 0; i < proof.V.length; i++) {
		    mem.temp = mulmod(mem.temp, mem.z, modulo); //temp = z^(j+2)
		    mem.k = addmod(mem.k, mulmod(mem.temp, mem.temp2, modulo), modulo);
		}
		
		//Final negation
		if (mem.k >= modulo) mem.k = mem.k % modulo;
		mem.k = modulo - mem.k;
		
		///Calculate inner product challenges
		mem.temp = mem.x_ip;
		for (i = 0; i < proof.L.length; i++) {
		    mem.temp = uint(keccak256(abi.encodePacked(mem.temp, proof.L[i].x, proof.L[i].y, proof.R[i].x, proof.R[i].y)));
		    mem.w[i] = mem.temp;
		}
		
		///Calculate inverse of inner product challenges
		mem.w_inv = Vector.Inverse(mem.w);
		
		///Compute Base Point Scalars
		mem.temp = mulmod(mem.z, mem.z, modulo); //z^(2 + i/N)
		mem.gScalars = new uint[](mem.MN);
		mem.hScalars = new uint[](mem.MN);
		for (i = 0; i < mem.MN; i++) {
		    mem.gScalar = proof.a;
		    mem.hScalar = mulmod(proof.b, mem.vpyi[i], modulo);
		    
		    uint bit = (1 << (mem.MN - 1));
		    for (j = 0; j < proof.L.length; j++) {
		        if (i & bit == 0) {
		            mem.gScalar = mulmod(mem.gScalar, mem.w_inv[j], modulo);
		            mem.hScalar = mulmod(mem.hScalar, mem.w[j], modulo);
		        }
		        else {
		            mem.gScalar = mulmod(mem.gScalar, mem.w[j], modulo);
		            mem.hScalar = mulmod(mem.hScalar, mem.w_inv[j], modulo);
		        }
		        
		        bit >>= 1;
		    }
		    
		    //Final gScalar
		    mem.gScalars[i] = addmod(mem.gScalar, mem.z, modulo);
		    
		    mem.temp2 = mulmod(mem.temp, mem.vp2[i % proof.N], modulo);
		    mem.temp2 = addmod(mem.temp2, mulmod(mem.z, mem.vpy[i], modulo), modulo);
		    mem.temp2 = mulmod(mem.temp2, mem.vpyi[i], modulo);
		    mem.hScalars[i] = addmod(mem.hScalar, modulo - mem.temp2, modulo);
		    
		    //Multiply temp with another z when moving to next commitment
		    if ((i % proof.N) == (proof.N-1)) {
		        mem.temp = mulmod(mem.temp, mem.z, modulo);
		    }
		}
		
		///Apply Stage 1 check
		//Does {(taux)*G1 + (t - [k + z*sum(vpy)])*H} == {sum([z^(j+2)] * V) + (x)*T1 + (x^2)*T2} ??
		
		///Apply Stage 2 check
		//Does {([t-a*b]*x_ip)*H + (A + x*S) + multiexp(Gi, gScalars) + multiexp(Hi, hScalars)} == {(mu)*G1} ??
		
		return true;
	}
	
	function GetHash(Data memory proof)
		public pure returns (bytes32 hash)
	{
	    //Serialize non-string data
		uint[] memory serialized = new uint[](7 + 2*(4 + proof.V.length + proof.L.length + proof.R.length));
		
		//Commitments
		uint i = 0;
		uint index = 0;
		for (i = 0; i < proof.V.length; i++) {
			serialized[index] = proof.V[i].x;
			serialized[index+1] = proof.V[i].y;
			index += 2;
		}
		
		//Signature Data
		serialized[index] = proof.A.x;
		serialized[index+1] = proof.A.y;
		serialized[index+2] = proof.S.x;
		serialized[index+3] = proof.S.y;
		serialized[index+4] = proof.T1.x;
		serialized[index+5] = proof.T1.y;
		serialized[index+6] = proof.T2.x;
		serialized[index+7] = proof.T2.y;
		index += 8;
		
		for (i = 0; i < proof.L.length; i++) {
			serialized[index] = proof.L[i].x;
			serialized[index+1] = proof.L[i].y;
			index += 2;
		}
		
		for (i = 0; i < proof.R.length; i++) {
			serialized[index] = proof.R[i].x;
			serialized[index+1] = proof.R[i].y;
			index += 2;
		}
		
		serialized[index] = proof.taux;
		serialized[index+1] = proof.mu;
		serialized[index+2] = proof.a;
		serialized[index+3] = proof.b;
		serialized[index+4] = proof.t;
		serialized[index+5] = proof.N;
		serialized[index+6] = uint(proof.asset_addr);
		//index += 7;
		
		//Calculate Hash
		return keccak256(abi.encodePacked(serialized));
	}
}