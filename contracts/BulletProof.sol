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
		G1Point.Data V;
		
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
	
	///Bullet Proof Verification Functions
	//Pre-check (i.e. check input proof for length, points on curve, etc.)
	function PreCheck(Data memory proof) internal pure returns (uint8 failure_code) {
		//Check inputs
		uint temp = proof.L.length; //logN
		if (temp == 0) return 1;
		if (proof.R.length != temp) return 2;
		
		uint N = (1 << temp);
		if (N == 0) return 3;
		if (N > 64) return 4;
		
		//Check points
		if (!proof.V.IsOnCurve()) return 5;
		if (!proof.A.IsOnCurve()) return 6;
		if (!proof.S.IsOnCurve()) return 7;
		if (!proof.T1.IsOnCurve()) return 8;
		if (!proof.T2.IsOnCurve()) return 9;
		
		for (uint i = 0; i < proof.L.length; i++) {
		    if (!proof.L[i].IsOnCurve()) return uint8(2*i + 9);
		    if (!proof.R[i].IsOnCurve()) return uint8(2*i + 10);
		}
	    
		//Success
		return 0;
	}
	
	//Generate Fiat Shamir Challenges
	function GetFiatShamirChallenges(Data memory proof)
	    internal pure returns (FiatShamirChallenges memory challenges)
	{
	    ///Do Fiat-Shamir
		challenges.y = uint(keccak256(abi.encodePacked(proof.V.x, proof.V.y, proof.A.x, proof.A.y, proof.S.x, proof.S.y)));
		challenges.z = uint(keccak256(abi.encodePacked(challenges.y)));
		challenges.x = uint(keccak256(abi.encodePacked(challenges.z, proof.T1.x, proof.T1.y, proof.T2.x, proof.T2.y)));
		challenges.x_ip = uint(keccak256(abi.encodePacked(challenges.x, proof.taux, proof.mu, proof.t)));
		
		//Calculate inner product challenges
		challenges.w = new uint[](proof.L.length);
		uint w_seed = challenges.x_ip;
		for (uint i = 0; i < proof.L.length; i++) {
		    w_seed = uint(keccak256(abi.encodePacked(w_seed, proof.L[i].x, proof.L[i].y, proof.R[i].x, proof.R[i].y)));
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
	function CalculateVectorPowers(uint y, uint yi, uint N)
	    internal pure returns (VectorPowers memory vp)
	{
	    vp.y = Vector.Powers(y, N);
	    vp.yi = Vector.Powers(yi, N);
	    vp.two = Vector.Powers(2, N);
	}
	
	//Calculate Stage 1
	//Check: y0*G + y1*Hasset = Y2 + Y3 + Y4
	//i.e. taux*G + [t - (k+z*sum{yp}]*Hasset = z^2*V + x*T1 + x^2*T2
	//Return true if equality holds, false if it does not
	function CalculateStage1Check(Data memory proof, FiatShamirChallenges memory c, VectorPowers memory v, G1Point.Data memory Hasset)
	    internal view returns (bool)
    {
        uint z2 = c.z.Square();
        uint yp_sum = Vector.Sum(v.y);
	    uint h_asset_scalar = Scalar.Add( z2.Multiply(yp_sum), z2.Multiply(c.z).Multiply(Vector.Sum(v.two)) ).Negate(); // k = -(z^2*vSum{vpy} + z^3*vSum{vp2})
	    h_asset_scalar = proof.t.Subtract(h_asset_scalar.Add(c.z.Multiply(yp_sum)));
	    
        G1Point.Data memory left = G1Point.GetG1().Multiply(proof.taux).Add(Hasset.Multiply(h_asset_scalar));
        G1Point.Data memory right = proof.V.Multiply(z2).Add(proof.T1.Multiply(c.x)).Add(proof.T2.Multiply(c.x.Square()));
        
        return left.Equals(right);
    }
	
	//Calculate Stage 2
	//Return Input scalars (z4, z5) and expected resulting G1Point (Pexp) for final exponentiation step
	//Where multiexp([Gi, Hi], z4, z5) = Pexp
	//Working toward verifying Z0 + z3*Hasset + Pexp = Z2 + z1*G
	function CalculateStage2Check(Data memory proof, FiatShamirChallenges memory c, VectorPowers memory v, G1Point.Data memory Hasset)
	    internal view returns (G1Point.Data memory Pexp, uint[] memory gi_scalars, uint[] memory hi_scalars)
	{
	    //multiexp([Gi, Hi], z4, z5) = -Z0 + z1*G + Z2 - z3*Hasset
        
        ///Find Pexp
	    //Subtact Z0 = A + x*S
	    Pexp = proof.A.Add(proof.S.Multiply(c.x)).Negate();
	    
	    //Add z1*G = mu*G
	    Pexp = Pexp.Add(G1Point.GetG1().Multiply(proof.mu));
	    
	    //Add Z2 = sum{wi^2*Li + wi^-2*Ri}
	    for (uint i = 0; i < proof.L.length; i++) {
	        Pexp = Pexp.Add(proof.L[i].Multiply(c.w[i].Square()));
	        Pexp = Pexp.Add(proof.R[i].Multiply(c.wi[i].Square()));
	    }
	    
	    //Subtract z3*Hasset = (t-a*b)*x_ip
	    Pexp = Pexp.Add(Hasset.Multiply(proof.t.Subtract(proof.a.Multiply(proof.b)).Multiply(c.x_ip)).Negate());
	    
        ///Calculate z4, z5
        uint z2 = c.z.Square();
        uint N = (1 << proof.L.length);
        gi_scalars = new uint[](N);
        hi_scalars = new uint[](N);
        for (uint i = 0; i < N; i++) {
            uint g_scalar = proof.a;
            uint h_scalar = proof.b.Multiply(v.yi[i]);
            
            uint bit = (1 << (N - 1));
            for (uint j = 0; j < proof.L.length; j++) {
                if (i & bit == 0) {
		            g_scalar = g_scalar.Multiply(c.wi[j]);
		            h_scalar = h_scalar.Multiply(c.w[j]);
		        }
		        else {
		            g_scalar = g_scalar.Multiply(c.w[j]);
		            h_scalar = h_scalar.Multiply(c.wi[j]);
		        }
		        
		        bit >>= 1;
            }
            
            //Finalize gi and hi scalars
            gi_scalars[i] = g_scalar.Add(c.z).Negate();
            
            uint temp = z2.Multiply(v.two[i]);
            temp = temp.Add(c.z.Multiply(v.y[i]));
            temp = temp.Multiply(v.yi[i]);
		    h_scalar = h_scalar.Subtract(temp);
		    hi_scalars[i] = h_scalar.Negate();
        }
	}
	
	//Calculate Stage 3: MultiExp
	//Check if multiexp([Gi, Hi], [z4, z5]) = Pexp
	function CalculateMultiExp(G1Point.Data memory Pexp, uint[] memory gi_scalars, uint[] memory hi_scalars)
	    internal view returns (bool)
	{
	    //Check inputs
	    if (gi_scalars.length == 0) return false;
	    if (gi_scalars.length != hi_scalars.length) return false;
	    if (!Pexp.IsOnCurve()) return false;
	    
	    //Do multi exponentiation
	    G1Point.Data memory right;
	    for (uint i = 0; i < gi_scalars.length; i++) {
	        //Gi = HashToPoint("Gi", [0...N-1])
	        //Hi = HashToPoint("Hi", [0...N-1])
			//Note, need to pre-calculate.  Costs are prohibitively high...
	        
	        right = right.Add(G1Point.FromX(uint(keccak256(abi.encodePacked("Gi", i)))).Multiply(gi_scalars[i]));
	        right = right.Add(G1Point.FromX(uint(keccak256(abi.encodePacked("Hi", i)))).Multiply(hi_scalars[i]));
	    }
	    
	    return Pexp.Equals(right);
	}
}