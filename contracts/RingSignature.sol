pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";

library RingSignature {
    using G1Point for G1Point.Data;
    
    struct Data {
	    //Message
	    string message;
	    
		//Inputs
		G1Point.Data[] input_pub_keys;
		G1Point.Data[] input_commitments;
		
		//Outputs
		G1Point.Data[] output_pub_keys;
		G1Point.Data[] output_commitments;
	
		//Signature Data
		uint c0;
		uint[] s;
		G1Point.Data[] key_images;
	}
	
	function IsValid(Data memory sig) public pure returns (bool) {
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
	    
		return true;
	}
	
	function Verify(Data memory sig) public view returns (bool) {
		if (!IsValid(sig)) return false;
		
		//Ring signature is actually n*(m+1), extra column will be assembled
		uint m = (sig.key_images.length - 1);
		uint n = (sig.input_pub_keys.length / m);
		
		//Generate last column of public keys (sum row pub keys and commitments then subtract off outputs commitments)
		uint i;
		uint j;
		uint index;
		
		//Calc negative sum of output commitments
		G1Point.Data memory point1 = sig.output_commitments[0];
		for (i = 1; i < sig.output_commitments.length; i++) {
		    point1 = point1.Add(sig.output_commitments[i]);
		}
		point1 = point1.Negate();
		
		//Calc rows
		G1Point.Data[] memory last_column_pub_keys = new G1Point.Data[](n);
		for (j = 0; j < n; j++) {
			index = j*m;
			last_column_pub_keys[j] = sig.input_pub_keys[index].Add(sig.input_commitments[index]);
			
			for (i = 1; i < m; i++) {
			    index += n;
			    last_column_pub_keys[j] = last_column_pub_keys[j].Add(sig.input_pub_keys[index]);
			    last_column_pub_keys[j] = last_column_pub_keys[j].Add(sig.input_commitments[index]);
			}
			
			//Subtract off output commitments
			last_column_pub_keys[j].Add(point1);
		}
		
		//Check ring signature
		//Start with first columns
		G1Point.Data memory point2;
		uint[] memory c0_inputs = new uint[](4*m + 4);
		uint ck;
		for (i = 0; i < m; i++) {
            ck = sig.c0;
            index = i*n;
            for (j = 0; j < n; j++) {
                //sk*G + ck*P
                point1 = G1Point.Shamir(    G1Point.GetG1(),                            sig.input_pub_keys[index+j],
                                            sig.s[index+j],                             ck                              );
                //sk*H(P) + ck*I
                point2 = G1Point.Shamir(    sig.input_pub_keys[index+j].HashToPoint(),  sig.key_images[i],
                                            sig.s[index+j],                             ck                              );
                
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
        
        //Do last column
        ck = sig.c0;
        index = m*n;
        for (j = 0; j < n; j++) {
            //sk*G + ck*P
            point1 = G1Point.Shamir(    G1Point.GetG1(),                        last_column_pub_keys[j],
                                        sig.s[index+j],                         ck                          );
            //sk*H(P) + ck*I
            point2 = G1Point.Shamir(    last_column_pub_keys[j].HashToPoint(),  sig.key_images[i],
                                        sig.s[index+j],                         ck                          );
            
            //Is this the last j? If so, do not calculate ck, just store points coords for borromean ring signature                         
            if (j == (n-1)) {
                index = 4*m;
                c0_inputs[index] = point1.x;
                c0_inputs[index+1] = point1.y;
                c0_inputs[index+2] = point2.x;
                c0_inputs[index+3] = point2.y;
            }
            else {
                ck = uint(keccak256(abi.encodePacked(sig.message, point1.x, point1.y, point2.x, point2.y)));
            }
        }
        
        //Check to see if ring is completed
        ck = uint(keccak256(abi.encodePacked(sig.message, c0_inputs)));
        return (ck == sig.c0);
	}
	
	function GetHash(Data memory sig)
		public pure returns (bytes32 hash)
	{
	    //Serialize non-string data
		uint[] memory serialized = new uint[](1 /*c0*/ + sig.s.length + 2*(sig.input_pub_keys.length + sig.input_commitments.length + sig.output_pub_keys.length + sig.output_commitments.length + sig.key_images.length));
		
		//Inputs
		uint i = 0;
		uint index = 0;
		for (i = 0; i < sig.input_pub_keys.length; i++) {
			serialized[index] = sig.input_pub_keys[i].x;
			serialized[index+1] = sig.input_pub_keys[i].y;
			index += 2;
		}
		
		for (i = 0; i < sig.input_commitments.length; i++) {
			serialized[index] = sig.input_commitments[i].x;
			serialized[index+1] = sig.input_commitments[i].y;
			index += 2;
		}
		
		//Outputs
		for (i = 0; i < sig.output_pub_keys.length; i++) {
			serialized[index] = sig.output_pub_keys[i].x;
			serialized[index+1] = sig.output_pub_keys[i].y;
			index += 2;
		}
		
		for (i = 0; i < sig.output_commitments.length; i++) {
			serialized[index] = sig.output_commitments[i].x;
			serialized[index+1] = sig.output_commitments[i].y;
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