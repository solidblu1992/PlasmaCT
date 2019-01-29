pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";
import "./Scalar.sol";

library SchnorrSignature {
    using G1Point for G1Point.Data;
    
    struct Data {
		string msg;
		G1Point.Data R;
		uint s;
	}
	
	function Recover(Data memory sig) public view returns (G1Point.Data memory P) {
		//Do input checks
		assert(sig.R.IsOnCurve());
		
		//sG = R + eP => P = e^-1 (R - sG)
		uint e_inv = Scalar.Inverse(uint(keccak256(abi.encodePacked(sig.R.x, sig.R.y, sig.msg))));
		P = sig.R.Add(G1Point.MultiplyG1(sig.s).Negate()).Multiply(e_inv);
		
		//Check P is On the Curve
		return P;
	}
	
	function IsValid(Data memory sig, G1Point.Data memory P) public view returns (bool) {
	    //Do input checks
		assert(P.IsOnCurve());
		return P.Equals(Recover(sig));
	}
	
	function GetHash(Data memory sig)
		public pure returns (bytes32 hash)
	{
		//Calculate Hash
		return keccak256(abi.encodePacked(sig.msg, sig.R.x, sig.R.y, sig.s));
	}
}