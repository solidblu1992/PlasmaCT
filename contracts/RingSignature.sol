pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";

library RingSignature {
    using G1Point for G1Point.Data;
    
    struct Data {
	    //Message
	    string message;
	    
		//Inputs
		G1Point.Data[] pub_keys;
	
		//Signature Data
		uint c0;
		uint[] s;
		G1Point.Data[] key_images;
	}
	
	function GetM(Data memory sig) internal pure returns (uint) {
		return sig.key_images.length;
	}
	
	function GetN(Data memory sig) internal pure returns (uint) {
		if (sig.pub_keys.length % sig.key_images.length != 0) return 0;
		
		return (sig.pub_keys.length / sig.key_images.length);
	}
	
	function IsValid(Data memory sig) internal view returns (bool) {
		//Check inputs
	    if (sig.pub_keys.length == 0) return false;
	    
	    //Check Key Images
	    uint m = sig.key_images.length;
	    if (m == 0) return false;
	    if (sig.pub_keys.length % m != 0) return false;
	    uint n = sig.pub_keys.length / m;
	    
	    if (m*n != sig.s.length) return false;
	    
	    //Do boundary checks
	    if (n > 16) return false;
	    if (m > 4) return false;
		
		//Check ring signature
		//Start with first columns
		uint[] memory c0_inputs = new uint[](4*m);
		
		G1Point.Data memory point1;
		G1Point.Data memory point2;
		uint ck;
		uint i;
		uint j;
		uint index;
		
		for (i = 0; i < m; i++) {
            ck = sig.c0;
            index = i*n;
            
            //Check that key image is on the curve
            if (!sig.key_images[i].IsOnCurve()) return false;
            
            for (j = 0; j < n; j++) {
                //Check that pub key is on the curve
                if (!sig.pub_keys[index+j].IsOnCurve()) return false;
                
                //sk*G + ck*P
                point1 = G1Point.Shamir(    G1Point.GetG1(),                        sig.pub_keys[index+j],
                                            sig.s[index+j],                         ck                      );
                //sk*H(P) + ck*I
                point2 = G1Point.Shamir(    sig.pub_keys[index+j].HashToPoint(),    sig.key_images[i],
                                            sig.s[index+j],                         ck                      );
                
                //Is this the last j? If so, do not calculate ck, just store points coords for borromean ring signature                         
                if (j == (n-1)) {
                    index = 4*i;
                    c0_inputs[index] = point1.x;
                    c0_inputs[index+1] = point1.y;
                    c0_inputs[index+2] = point2.x;
                    c0_inputs[index+3] = point2.y;
                }
                else {
                    ck = uint(keccak256(abi.encodePacked(sig.message, point1.x, point1.y, point2.x, point2.y)));
                }
            }
        }
        
        //Check to see if ring is completed
        ck = uint(keccak256(abi.encodePacked(sig.message, c0_inputs)));
        return (ck == sig.c0);
	}
	
	function GetHash(Data memory sig)
		internal pure returns (bytes32 hash)
	{
	    //Serialize non-string data
		uint[] memory serialized = new uint[](1 /*c0*/ + sig.s.length + 2*(sig.pub_keys.length + sig.key_images.length));
		
		//Inputs
		uint i = 0;
		uint index = 0;
		for (i = 0; i < sig.pub_keys.length; i++) {
			serialized[index] = sig.pub_keys[i].x;
			serialized[index+1] = sig.pub_keys[i].y;
			index += 2;
		}
		
		//Signature Data
		serialized[index] = sig.c0;
		index++;
		
		for (i = 0; i < sig.s.length; i++) {
			serialized[index] = sig.s[i];
			index++;
		}
		
		for (i = 0; i < sig.key_images.length; i++) {
			serialized[index] = sig.key_images[i].x;
			serialized[index+1] = sig.key_images[i].y;
			index++;
		}
		
		//Calculate Hash
		return keccak256(abi.encodePacked(sig.message, serialized));
	}
}