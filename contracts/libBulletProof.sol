pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";
import "./Scalar.sol";
import "./Vector.sol";

library BulletProof {
    using G1Point for G1Point.Data;
    using Scalar for uint;
    
    struct Data {	    
		//Comitment
		address asset_addr;
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
	}
	
	struct FiatShamirChallenges {
	    //Scalars
	    uint y;
	    uint z;
	    uint x;
	    uint x_ip;
	    uint[] w;
	    
	    //Inverses
	    uint yi;
	    uint[] wi;
	}
	
	struct VectorPowers {
	    uint[] y;       //1, y, y^2, ... y^(N-1)
	    uint[] yi;      //1, y^-1, y^-2, ... y^(1-N)
	    uint[] two;     //1, 2, 4, ..., 2^(N-1)
	}
	
	function GetAssetH(address asset_addr) internal view returns (G1Point.Data memory) {
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
	
	/*
     * GiHi Merkel Tree:
     * Level 0: 0x85d8262392522426148186dac9768b3cc51d4b35eeba4c603a9ff11deb53976a
     * 
     * Level 1: 0x9004559687a1c006a20791488af47bd539cba563226348eb449c276a982ecf71
     *          0x30110634e8710f1d38e92c18ff901a68be5538c784687c971d79743d0e20327f
     * 
     * Level 2: 0x3891a4d799d97bcbdee141a8ad6b4dc8bebc345e9e9e07e1c13f841f2f05c3d6
     *          0x3de9bf738f68b9f86e96b5ef6460b7119c5edb414bcd241176f8a5cadd185f36
     *          0x82d3b33167dcaca50b44d1a2a3c69f1eee250cc4618b7d82f835dca9b2db0d4e
     *          0xe07bd318f8c2120950240117625beb19f68e2739d5ab312ccdec62b44ab9768a
     * 
     * Each Level 2 hash is the hash of 16 Gi and Hi pairs
     * e.g. keccak256(Gi[0], Hi[0], Gi[1], Hi[1], ..., Gi[15], Hi[15])
     */
	function GetGiHiMerkelRoot() internal pure returns (bytes32 root) {
	    root = 0x85d8262392522426148186dac9768b3cc51d4b35eeba4c603a9ff11deb53976a;
	}
	
	function VerifyGiHiMerkelLeaf(bytes memory leaf_data, uint8 chunk_index, bytes32 level2_hash, bytes32 level1_hash) internal pure returns (bool) {
	    //Check input
	    if (chunk_index > 3) return false;
	    
	    //Calculate leaf hash (level 2)
	    bytes32 leaf_hash = keccak256(abi.encodePacked(leaf_data));
	    
	    //Calculate level 1 hash
	    if (chunk_index % 2 == 0) {
	        leaf_hash = keccak256(abi.encodePacked(leaf_hash, level2_hash));
	    }
	    else {
	        leaf_hash = keccak256(abi.encodePacked(level2_hash, leaf_hash));
	    }
	    
	    //Calculate level 0 (root) hash
	    if ((chunk_index / 2) % 2 == 0) {
	        leaf_hash = keccak256(abi.encodePacked(leaf_hash, level1_hash));
	    }
	    else {
	        leaf_hash = keccak256(abi.encodePacked(level1_hash, leaf_hash));
	    }
	    
	    return (leaf_hash == GetGiHiMerkelRoot());
	}
	
	///Bullet Proof Verification Functions
	//Pre-check (i.e. check input proof for length, points on curve, etc.)
	function PreCheck(Data memory proof) internal pure returns (uint16 failure_code) {
		//Check inputs
		uint temp = proof.L.length; //logMN
		if (temp == 0) return 1;
		if (proof.R.length != temp) return 2;
		
		uint MN = (1 << temp);
		if (MN == 0) return 3;
		if (MN > 64) return 4;
		
		if (proof.V.length == 0) return 5;     //Must have at least one commitment
		if (MN % proof.V.length != 0) return 6; //M = V.length, MN must be divisible by M
		
		//Check points - must be on curve
		if (!proof.A.IsOnCurve()) return 7;
		if (!proof.S.IsOnCurve()) return 8;
		if (!proof.T1.IsOnCurve()) return 9;
		if (!proof.T2.IsOnCurve()) return 10;
		
		for (uint i = 0; i < proof.V.length; i++) {
		    if (!proof.V[i].IsOnCurve()) return uint8(128 + i);
		}
		
		for (uint i = 0; i < proof.L.length; i++) {
		    if (!proof.L[i].IsOnCurve()) return uint8(256 + 2*i);
		    if (!proof.R[i].IsOnCurve()) return uint8(256 + 2*i + 1);
		}
	    
		//Success
		return 0;
	}
	
	//Generate Fiat Shamir Challenges
	function GetFiatShamirChallenges(Data memory proof)
	    internal pure returns (FiatShamirChallenges memory challenges)
	{
	    ///Do Fiat-Shamir
	    uint Ncurve = G1Point.GetN();
		challenges.y = uint(keccak256(abi.encodePacked(G1Point.PointArrayToUintArray(proof.V), proof.A.x, proof.A.y, proof.S.x, proof.S.y))) % Ncurve;
		challenges.z = uint(keccak256(abi.encodePacked(challenges.y))) % Ncurve;
		challenges.x = uint(keccak256(abi.encodePacked(challenges.z, proof.T1.x, proof.T1.y, proof.T2.x, proof.T2.y))) % Ncurve;
		challenges.x_ip = uint(keccak256(abi.encodePacked(challenges.x, proof.taux, proof.mu, proof.t))) % Ncurve;
		
		//Calculate inner product challenges
		challenges.w = new uint[](proof.L.length);
		uint w_seed = challenges.x_ip;
		for (uint i = 0; i < proof.L.length; i++) {
		    w_seed = uint(keccak256(abi.encodePacked(w_seed, proof.L[i].x, proof.L[i].y, proof.R[i].x, proof.R[i].y))) % Ncurve;
		    challenges.w[i] = w_seed;
		}
		
		///Calculate inverse of y and w[]
		//Compact w's and y.
	    uint[] memory inverses = new uint[](1 + challenges.w.length);
	    for (uint i = 0; i < challenges.w.length; i++) {
	        inverses[i] = challenges.w[i];
	    }
	    inverses[challenges.w.length] = challenges.y;
	    
	    //Calculate Inverses using one modulo inverse
	    inverses = Vector.Inverse(inverses);
	    
	    //Split up yi and wi
	    challenges.wi = new uint[](challenges.w.length);
	    for (uint i = 0; i < challenges.wi.length; i++) {
	        challenges.wi[i] = inverses[i];
	    }
	    
	    challenges.yi = inverses[challenges.w.length];
	}
	
	//Generate vector powers of 2, y, and inv(y); N bits long
	function GetVectorPowers(uint y, uint yi, uint N, uint M)
	    internal pure returns (VectorPowers memory vp)
	{
	    vp.y = Vector.Powers(y, N*M);
	    vp.yi = Vector.Powers(yi, N*M);
	    vp.two = Vector.Powers(2, N);
	}
	
	//Calculate Stage 1
	//Check: y0*G + y1*Hasset = Y2 + Y3 + Y4
	//i.e. taux*G + [t - (k+z*sum{yp}]*Hasset = z^2*V + x*T1 + x^2*T2
	//Return true if equality holds, false if it does not
	function CalculateStage1Check(Data memory proof, FiatShamirChallenges memory c, VectorPowers memory v, G1Point.Data memory Hasset)
	    internal view returns (bool)
    {
        uint yp_sum = Vector.Sum(v.y);
        
        //Find k first
        // k = -(z^3*vSum{vp2} + z^2*vSum{vpy})
        uint zk = c.z.Square();
	    uint h_asset_scalar = 0;
	    for (uint i = 0; i < proof.V.length; i++) {
	        zk = zk.Multiply(c.z);  //z^3, z^4, ..., z^(2+M)
	        h_asset_scalar = h_asset_scalar.Add(zk);
	    }
	    
	    //Reset zk to z^2
	    zk = c.z.Square();
	    h_asset_scalar = h_asset_scalar.Multiply(Vector.Sum(v.two)).Add(zk.Multiply(yp_sum)).Negate();
	    
	    //Finish off h_asset_scalar
	    h_asset_scalar = proof.t.Subtract(h_asset_scalar.Add(c.z.Multiply(yp_sum)));
	    
        G1Point.Data memory left = G1Point.GetG1().Multiply(proof.taux).Add(Hasset.Multiply(h_asset_scalar));
        
        //Multiply each commitment by z(j+2) and add to right
        //zk starts at 2, and is incremented by 1 every step
        G1Point.Data memory right = proof.V[0].Multiply(zk);
        for (uint i = 1; i < proof.V.length; i++) {
            zk = zk.Multiply(c.z);
            right = right.Add(proof.V[i].Multiply(zk));
        }
        
        right = right.Add(proof.T1.Multiply(c.x)).Add(proof.T2.Multiply(c.x.Square()));
        
        return left.Equals(right);
    }
	
	//Calculate Stage 2
	//Return Input scalars (z4, z5) and expected resulting G1Point (Pexp) for final exponentiation step
	//Where multiexp([Gi, Hi], z4, z5) = Pexp
	//Working toward verifying Z0 + z3*Hasset + Pexp = Z2 + z1*G
	function CalculateStage2_MultiExpScalars(Data memory proof, FiatShamirChallenges memory c, VectorPowers memory v)
	    internal pure returns (uint[] memory gi_scalars, uint[] memory hi_scalars)
	{
        ///Calculate z4, z5
        uint zk = c.z;
        uint MN = (1 << proof.L.length);
        gi_scalars = new uint[](MN);
        hi_scalars = new uint[](MN);
        for (uint i = 0; i < MN; i++) {
            gi_scalars[i] = proof.a;
            hi_scalars[i] = proof.b.Multiply(v.yi[i]);
            
            uint bit = (MN >> 1);
            for (uint j = 0; j < proof.L.length; j++) {
                if (i & bit == 0) {
		            gi_scalars[i] = gi_scalars[i].Multiply(c.wi[j]);
		            hi_scalars[i] = hi_scalars[i].Multiply(c.w[j]);
		        }
		        else {
		            gi_scalars[i] = gi_scalars[i].Multiply(c.w[j]);
		            hi_scalars[i] = hi_scalars[i].Multiply(c.wi[j]);
		        }
		        
		        bit >>= 1;
            }
            
            ///Finalize gi and hi scalars
            ///gi scalar is simple
            gi_scalars[i] = gi_scalars[i].Add(c.z).Negate();
            
            ///hi scalar calculation
            uint temp;
            
            //N == 1 simplification
            if (v.two.length == 1) {
                //Equation
                //h[i] = (z^[2+i])*(y^-i) + z - h_scalar
                
                //Set zk to z^2
                zk = zk.Multiply(c.z);
                temp = zk;
            }
            //M == 1 simplification
            else if (proof.V.length == 1) {
                //Equation
                //h[i] = (2^i)*(z^2)*(y^-i) + z - h_scalar
                temp = v.two[i].Multiply(c.z.Square());
            }
            //N > 1 and M > 1
            else {
                //Equation
                //h[i] = (z^[2+i/N])*(2^[i%N])*(y^-i) + z - h_scalar
                temp = c.z.Power(2+i/v.two.length).Multiply(v.two[i%v.two.length]);
            }
            
            //Multiplication of yi, addition of z, and subtraction is common to all variants
		    hi_scalars[i] = temp.Multiply(v.yi[i]).Add(c.z).Subtract(hi_scalars[i]);
        }
	}
	
	function CalculateStage2_ExpectedMultiExpResult(Data memory proof, FiatShamirChallenges memory c, G1Point.Data memory Hasset)
	    internal view returns (G1Point.Data memory Pexp)
	{
	    //multiexp([Gi, Hi], z4, z5) = -Z0 + z1*G - Z2 - z3*Hasset
        
        ///Find Pexp
	    //Subtact Z0 = A + x*S
	    Pexp = proof.A.Add(proof.S.Multiply(c.x)).Negate();
	    
	    //Add z1*G = mu*G
	    Pexp = Pexp.Add(G1Point.GetG1().Multiply(proof.mu));
	    
	    //Subtract Z2 = sum{wi^2*Li + wi^-2*Ri}
	    for (uint i = 0; i < proof.L.length; i++) {
	        Pexp = Pexp.Subtract(proof.L[i].Multiply(c.w[i].Square()));
	        Pexp = Pexp.Subtract(proof.R[i].Multiply(c.wi[i].Square()));
	    }
	    
	    //Subtract z3*Hasset = (t-a*b)*x_ip
	    Pexp = Pexp.Subtract(Hasset.Multiply(proof.t.Subtract(proof.a.Multiply(proof.b)).Multiply(c.x_ip)));
	}
	
	//Calculate Stage 3: MultiExp
	//Check if multiexp([Gi, Hi], [gi_scalars, hi_scalars])
	//Can be done in pieces
	function CalculateMultiExp(G1Point.Data memory P_initial, uint[] memory gi_scalars, uint[] memory hi_scalars, uint start, uint count)
	    internal view returns (G1Point.Data memory P_out)
	{
	    //Check inputs
	    require(gi_scalars.length > 0);
	    require(gi_scalars.length == hi_scalars.length);
	    require(start < gi_scalars.length);
	    require(count <= gi_scalars.length);
	    require((start+count) <= gi_scalars.length);
	    
	    //Set initial point if given (to allow multiexp to be broken up into multiple steps)
	    if (!P_initial.IsZero()) {
	        require(P_initial.IsOnCurve());
	        (P_out.x, P_out.y) = (P_initial.x, P_initial.y);
	    }
	    
	    //Do multi exponentiation
	    for (uint i = start; i < (start+count); i++) {
	        //Gi = HashToPoint("Gi", [0...N-1])
	        //Hi = HashToPoint("Hi", [0...N-1])
	        
	        P_out = P_out.Add(G1Point.FromX(uint(keccak256(abi.encodePacked("Gi", i)))).Multiply(gi_scalars[i]));
	        P_out = P_out.Add(G1Point.FromX(uint(keccak256(abi.encodePacked("Hi", i)))).Multiply(hi_scalars[i]));
	    }
	}
	
	function Deserialize(bytes memory b) internal pure returns (BulletProof.Data memory proof) {
	    //Buffers and offsets
	    uint offset = 0x20;
	    uint x;
	    uint y;
	    
	    //Get M, allocate V[]
	    assembly { x := mload(add(b, offset)) }
	    proof.V = new G1Point.Data[](x);
	    
	    //Get logMN, allocate L[] and R[]
	    assembly { x := mload(add(b, offset)) }
	    proof.L = new G1Point.Data[](x);
	    proof.R = new G1Point.Data[](x);
	    offset += 0x20;
	    
	    //Get asset_addr
	    assembly { x := mload(add(b, offset)) }
	    proof.asset_addr = address(x);
	    offset += 0x20;
	    
        //Get V
        for (uint i = 0; i < proof.V.length; i++) {
            assembly {
                x := mload(add(b, offset))
                y := mload(add(b, add(offset, 0x20)))
            }
            proof.V[i].x = x;
            proof.V[i].y = y;
            offset += 0x40;
        }
        
        //Get A
        assembly {
            x := mload(add(b, offset))
            y := mload(add(b, add(offset, 0x20)))
        }
        proof.A.x = x;
        proof.A.y = y;
        offset += 0x40;
        
        //Get S
        assembly {
            x := mload(add(b, offset))
            y := mload(add(b, add(offset, 0x20)))
        }
        proof.S.x = x;
        proof.S.y = y;
        offset += 0x40;
        
        //Get T1
        assembly {
            x := mload(add(b, offset))
            y := mload(add(b, add(offset, 0x20)))
        }
        proof.T1.x = x;
        proof.T1.y = y;
        offset += 0x40;
        
        //Get T2
        assembly {
            x := mload(add(b, offset))
            y := mload(add(b, add(offset, 0x20)))
        }
        proof.T2.x = x;
        proof.T2.y = y;
        offset += 0x40;
        
        //Get L
        for (uint i = 0; i < proof.L.length; i++) {
            assembly {
                x := mload(add(b, offset))
                y := mload(add(b, add(offset, 0x20)))
            }
            proof.L[i].x = x;
            proof.L[i].y = y;
            offset += 0x40;
        }
        
        //Get R
        for (uint i = 0; i < proof.R.length; i++) {
            assembly {
                x := mload(add(b, offset))
                y := mload(add(b, add(offset, 0x20)))
            }
            proof.R[i].x = x;
            proof.R[i].y = y;
            offset += 0x40;
        }
        
        //Get taux
        assembly { x := mload(add(b, offset)) }
        proof.taux = x;
        offset += 0x20;
        
        //Get mu
        assembly { x := mload(add(b, offset)) }
        proof.mu = x;
        offset += 0x20;
        
        //Get a
        assembly { x := mload(add(b, offset)) }
        proof.a = x;
        offset += 0x20;
        
        //Get b
        assembly { x := mload(add(b, offset)) }
        proof.b = x;
        offset += 0x20;
        
        //Get t
        assembly { x := mload(add(b, offset)) }
        proof.t = x;
        offset += 0x20;
	}
}
