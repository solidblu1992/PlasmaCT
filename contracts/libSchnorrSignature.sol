pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";
import "./Scalar.sol";
import "./Vector.sol";

library SchnorrSignature {
    using G1Point for G1Point.Data;
    
    struct Data {
		G1Point.Data R;
		uint s;
		string message;
	}
	
	//Recover public key required to make Schnorr Signature valid
	function Recover(Data memory sig) internal view returns (G1Point.Data memory P) {
		//Do input checks
		assert(sig.R.IsOnCurve());
		
		//sG = R - eP
		//P = e^-1 (R - sG)
		uint e_inv = Scalar.Inverse(uint(keccak256(abi.encodePacked(sig.R.x, sig.R.y, sig.message))));
		P = sig.R.Add(G1Point.MultiplyG1(sig.s).Negate()).Multiply(e_inv);
	}
	
	//Recover public keys from multiple Schnorr Signature (using only one mod-inverses)
	function RecoverMultiple(Data[] memory sig) internal view returns(G1Point.Data[] memory P) {
		//Trivial Cases
		if (sig.length == 0) {
			P = new G1Point.Data[](0);
		}
		else if (sig.length == 1) {
			P = new G1Point.Data[](1);
			P[0] = Recover(sig[0]);
		}

		//The main optimization here is that only one mod-inverse is necessary
		uint[] memory e_inv = new uint[](sig.length);
		
		uint i;
		for (i = 0; i < sig.length; i++) {
			//Check that R is on the curve
			assert(sig[i].R.IsOnCurve());
			
			//Get e-value
			e_inv[i] = uint(keccak256(abi.encodePacked(sig[i].R.x, sig[i].R.y, sig[i].message)));
		}
		
		//Calculate batch inverse
		e_inv = Vector.Inverse(e_inv);
		
		//Calculate Public Keys
		P = new G1Point.Data[](sig.length);
		
		for (i = 0; i < sig.length; i++) {
			P[i] = sig[i].R.Add(G1Point.MultiplyG1(sig[i].s).Negate()).Multiply(e_inv[i]);
		}
	}
	
	//Recover sum of public keys from multiple Schnorr Signatures (using only one mod inverse and N-1 EC multiplications)
	function RecoverMultipleSum(Data[] memory sig) internal view returns (G1Point.Data memory P) {
		//Trivial Cases
		if (sig.length == 0) {
			P = G1Point.Data(0, 0);
		}
		else if (sig.length == 1) {
			P = Recover(sig[0]);
		}

		//The main optimizations here are that
		//1: only one mod-inverse is necessary,
		//2: we can get by with only (N-1) multiplications vs (2N)
		
		//sG = R - eP
		//P = e^-1 (R - sG)
		//sum {P} = e0^-1(R) + e1^-1(R) + ... - (s0 + s1 + ...)G
		uint[] memory e_inv = new uint[](sig.length);
		
		uint i;
		for (i = 0; i < sig.length; i++) {
			//Check that R is on the curve
			assert(sig[i].R.IsOnCurve());
			
			//Get e-value
			e_inv[i] = uint(keccak256(abi.encodePacked(sig[i].R.x, sig[i].R.y, sig[i].message)));
		}
		
		//Calculate batch inverse
		e_inv = Vector.Inverse(e_inv);
		
		//Sum (e0^-1(R) + e1^-1(R) + ...) and (s0 + s1 + ...)
		
		//Calculate Public Keys
		uint s_sum = sig[0].s;
		P = sig[0].R.Multiply(e_inv[0]);
		
		for (i = 1; i < sig.length; i++) {
		    //Add sk
		    s_sum = Scalar.Add(s_sum, sig[i].s);
		    
		    //Add ek^-1(R)
		    P = P.Add(sig[i].R.Multiply(e_inv[i]));
		}
		
		//Compute s_sum*G1 and subtract to P
		P = P.Add(G1Point.MultiplyG1(s_sum).Negate());
	}
	
	function IsValid(Data memory sig, G1Point.Data memory P) internal view returns (bool) {
	    //Do input checks
		if (!P.IsOnCurve()) return false;
		
		//Does P match the required Public Key?
		return P.Equals(Recover(sig));
	}
	
	function AreValid(Data[] memory sig, G1Point.Data[] memory P) internal view returns (bool) {
		//Do input checks
		if (sig.length == 0) return false;
		if (sig.length != P.length) return false;
		
		//For a valid signature: sum{s}*G = sum{R} - sum{ekPk}
		//or sum{ekPk} = sum{R} - sum{s}*G
		G1Point.Data memory P_sum_right = RecoverMultipleSum(sig);
		
		//Calculate sum{Pk}
		G1Point.Data memory P_sum_left = P[0];
		for (uint i = 1; i < sig.length; i++) {
		    if (!P[i].IsOnCurve()) return false;
			P_sum_left = P_sum_left.Add(P[i]);
		}
		
		return P_sum_left.Equals(P_sum_right);
	}
	
	function GetHash(Data memory sig) internal pure returns (bytes32 hash) {
		//Calculate Hash
		return keccak256(abi.encodePacked(sig.R.x, sig.R.y, sig.s, sig.message));
	}
	
	//Serialze Schnorr Signature into bytes
	function Serialize(Data memory sig) internal pure returns (bytes memory b) {
	    bytes memory msg_bytes = bytes(sig.message);
	    
	    //If message is blank, do not encode
	    if (msg_bytes.length == 0) {
	        b = abi.encodePacked(sig.R.Serialize(), sig.s);
	    }
	    else {
	        //Note, need to encode message length for bytes in order for string conversion to work
	        b = abi.encodePacked(sig.R.Serialize(), sig.s, msg_bytes.length, msg_bytes);
	    }
	}
	
	//Deserialize Schnorr Signature from bytes
	function Deserialize(bytes memory b) internal pure returns (Data memory sig) {
	    //Get R
	    bytes memory b_temp;
	    assembly { b_temp := add(b, 32) }
	    sig.R = G1Point.Deserialize(b);
	    
	    //Get S
	    uint temp;
	    assembly { temp := mload(add(b, 96)) }
	    sig.s = temp;
	    
	    //If message is not blank
	    if (b.length > 96) {
    	    //Get message
    	    assembly { b_temp := add(b, 128) }
    	    sig.message = string(b_temp);
	    }
	}

	//Deserialize a G1Point and a Schnorr Signature from bytes
	function Deserialize_wG1Point(bytes memory sig_w_point_bytes)
		internal pure returns (G1Point.Data memory point, Data memory sig)
	{
	    //Get point
	    /*
	    //Store G1Point length so that Deserialize sees 64 bytes instead of total signature length
	    //Store original bytes length for safe keeping 
	    uint b_length = sig_w_point_bytes.length;
	    assembly { mstore(sig_w_point_bytes, 64) }
	    */
	    point = G1Point.Deserialize(sig_w_point_bytes);
	    
	    //Get signature
	    bytes memory b;
	    assembly {
	        b := add(sig_w_point_bytes, 64)
	    }
		sig = Deserialize(b);
	}
}
