pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";

library RingSignature {
    using G1Point for G1Point.Data;
    
    struct Data {
	    //Message
	    string message;
	    
		//Inputs
		G1Point.Data[][] pub_keys;
	
		//Signature Data
		uint c0;
		uint[][] s;
		G1Point.Data[] key_images;
	}
	
	function GetM(Data memory sig) internal pure returns (uint) {
		return sig.pub_keys.length;
	}
	
	function GetN(Data memory sig) internal pure returns (uint) {
	    require(sig.pub_keys.length > 0);
	    return sig.pub_keys[0].length;
	}
	
	function IsValid(Data memory sig) internal view returns (bool) {
		//Check inputs
	    if (sig.pub_keys.length == 0) return false;
	    
	    //Check Key Images and Public Key dimensions
	    uint m = sig.pub_keys.length;
	    if (m == 0) return false;
	    if (sig.key_images.length != m) return false;
	    
	    uint n = sig.pub_keys[0].length;
	    if (n == 0) return false;
	    
	    if (m != sig.s.length) return false;
	    if (n != sig.s[0].length) return false;
	    
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
                if (!sig.pub_keys[i][j].IsOnCurve()) return false;
                
                //sk*G + ck*P
                point1 = G1Point.Shamir(    G1Point.GetG1(),                    sig.pub_keys[i][j],
                                            sig.s[i][j],                        ck                      );
                //sk*H(P) + ck*I
                point2 = G1Point.Shamir(    sig.pub_keys[i][j].HashToPoint(),   sig.key_images[i],
                                            sig.s[i][j],                        ck                      );
                
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
	
	function GetHash(Data memory sig) internal pure returns (bytes32 hash)	{
	    //Serialize non-string data
	    uint m = sig.pub_keys.length;
	    uint n = sig.pub_keys[0].length;
		uint[] memory serialized = new uint[](3*m*n + 2*m + 1);   //c0 + s[m][n] + 2*(pub_keys[m][n]+key_images[m])
		
		//Inputs
		uint i = 0;
		uint j = 0;
		uint index = 0;
		for (i = 0; i < m; i++) {
		    for (j = 0; j  < n; j++) {
    			serialized[index] = sig.pub_keys[i][j].x;
    			serialized[index+1] = sig.pub_keys[i][j].y;
    			index += 2;
		    }
		}
		
		//Signature Data
		serialized[index] = sig.c0;
		index++;
		
		for (i = 0; i < m; i++) {
		    for (j = 0; j < n; j++) {
    			serialized[index] = sig.s[i][j];
    			index++;
		    }
		}
		
		for (i = 0; i < m; i++) {
			serialized[index] = sig.key_images[i].x;
			serialized[index+1] = sig.key_images[i].y;
			index++;
		}
		
		//Calculate Hash
		return keccak256(abi.encodePacked(sig.message, serialized));
	}

    function FromBytes(bytes memory b) internal pure returns (Data memory sig) {
        //Format: m, n, pub_keys[m][n], c0, s[m*n], key_images[m], message
        uint offset = 32;
        uint m;
        assembly { m := mload(add(b, offset)) }
        offset += 0x20;
        
        require(m > 0);
        
        uint n;
        assembly { m := mload(add(b, offset)) }
        offset += 0x20;
        
        require(n > 0);
        
        //Allocate and populate public key array
        sig.pub_keys = new G1Point.Data[][](m);
        
        uint buffer;
        for (uint i = 0; i < m; i++) {
            sig.pub_keys[i] = new G1Point.Data[](n);
            
            for (uint j = 0; j < n; j++) {
                assembly { buffer := mload(add(b, offset)) }
                sig.pub_keys[i][j].x = buffer;
                offset += 0x20;
                
                assembly { buffer := mload(add(b, offset)) }
                sig.pub_keys[i][j].y = buffer;
                offset += 0x20;
            }   
        }
        
        //Get c0
        assembly { buffer := mload(add(b, offset)) }
        sig.c0 = buffer;
        offset += 0x20;
        
        //Get s[][]
        sig.s = new uint[][](m);
        for (uint i = 0; i < m; i++) {
            sig.s[i] = new uint[](n);
            
            for (uint j = 0; j < n; j++) {
                assembly { buffer := mload(add(b, offset)) }
                sig.s[i][j] = buffer;
                offset += 0x20;
            }   
        }
        
        //Get key images
        sig.key_images = new G1Point.Data[](m);
        for (uint i = 0; i < m; i++) {
            assembly { buffer := mload(add(b, offset)) }
            sig.key_images[i].x = buffer;
            offset += 0x20;
            
            assembly { buffer := mload(add(b, offset)) }
            sig.key_images[i].y = buffer;
            offset += 0x20;
        }
        
        //Get message
        bytes memory b_temp;
        assembly { b_temp := add(b, offset) }
        sig.message = string(b_temp);
    }
}
