pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";
import "./Scalar.sol";
import "./Vector.sol";

library SchnorrSignature {
    using G1Point for G1Point.Data;
    
    struct Data {
		string msg;
		G1Point.Data R;
		uint s;
	}
	
	function Recover(Data memory sig) internal view returns (G1Point.Data memory P) {
		//Do input checks
		assert(sig.R.IsOnCurve());
		
		//sG = R - eP
		//P = e^-1 (R - sG)
		uint e_inv = Scalar.Inverse(uint(keccak256(abi.encodePacked(sig.R.x, sig.R.y, sig.msg))));
		P = sig.R.Add(G1Point.MultiplyG1(sig.s).Negate()).Multiply(e_inv);
	}
	
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
			e_inv[i] = uint(keccak256(abi.encodePacked(sig[i].R.x, sig[i].R.y, sig[i].msg)));
		}
		
		//Calculate batch inverse
		e_inv = Vector.Inverse(e_inv);
		
		//Calculate Public Keys
		P = new G1Point.Data[](sig.length);
		
		for (i = 0; i < sig.length; i++) {
			P[i] = sig[i].R.Add(G1Point.MultiplyG1(sig[i].s).Negate()).Multiply(e_inv[i]);
		}
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
		
		uint i;
		for (i = 0; i < P.length; i++) {
			if (!P[i].IsOnCurve()) return false;
		}
		
		//For a valid signature: sum{s}*G = sum{R} - sum{ekPk}
		//or sum{ekPk} = sum{R} - sum{s}*G
		//Note: Don't use RecoverMultiple as additional optimzations can be done
		//e.g.  can sum s-values as scalars instead of G1Points
		//      this also includes the single mod-inverse optimization
		uint[] memory e_inv = new uint[](sig.length);
		
		G1Point.Data memory right = sig[0].R;
		uint s_sum = sig[0].s;
		
		for (i = 0; i < sig.length; i++) {
			//Check that R is on the curve
			assert(sig[i].R.IsOnCurve());
			
			//Get e-value
			e_inv[i] = uint(keccak256(abi.encodePacked(sig[i].R.x, sig[i].R.y, sig[i].msg)));
			
			if (i > 0) {
				//i == 0: the initial value is already stored in s_sum and right before the for loop
				
				//Sum s-values
				s_sum = Scalar.Add(s_sum, sig[i].s);
				
				//Sum R-points
				right = right.Add(sig[i].R);
			}
		}
		
		//Subtract of sG
		right = right.Add(G1Point.MultiplyG1(s_sum).Negate());
		
		//Calculate batch inverse
		e_inv = Vector.Inverse(e_inv);
		
		//Calculate sum{ekPk}
		G1Point.Data memory left;
				
		for (i = 0; i < sig.length; i++) {
			left = left.Add(G1Point.Multiply(P[i], e_inv[i]));
		}
		
		return left.Equals(right);
	}
	
	function GetHash(Data memory sig)
		internal pure returns (bytes32 hash)
	{
		//Calculate Hash
		return keccak256(abi.encodePacked(sig.msg, sig.R.x, sig.R.y, sig.s));
	}
}