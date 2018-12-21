pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

library G1Point {
	struct Data {
	    uint x;
	    uint y;
	}
	
	uint256 constant private N = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;
	uint256 constant private P = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;
	uint256 constant private a = 0xc19139cb84c680a6e14116da060561765e05aa45a1c72a34f082305b61f3f52; // (p+1)/4
	
	function FromX(uint x) public view returns (Data memory) {
	    uint p = P;
	    x = x % p;
	    
	    uint[] memory data = new uint[](6);
	    data[0] = 0x20;
	    data[1] = 0x20;
	    data[2] = 0x20;
	    //data[3] = 0;
	    data[4] = a;
	    data[5] = p;
	    
        bool onCurve = false;
        while(!onCurve) {
            //Get y coordinate
    	    data[3] = addmod(mulmod(mulmod(x, x, p), x, p), 3, p);
    	    
    	    assembly {
    	        //Call Big Int Mod Exp: (y_squared)^a % p, store y in data[3]
        	    let success := staticcall(sub(gas, 2000), 0x05, add(data, 0x20), 0xC0, add(data, 0x80), 0x20)
    	    }
    	    
    	    //Check y coordinate
    	    onCurve = IsOnCurve(Data(x, data[3]));
    	    if (!onCurve) {
    	        x = addmod(x, 1, p);
    	    }
        }
        
        return Data(x, data[3]);
	}
	
	function IsValid(Data memory point) public pure returns (bool) {
	    if (point.x == 0) return false;
	    if (point.y == 0) return false;
	    
	    //Passed
	    return true;
	}
	
	function IsOnCurve(Data memory point) public pure returns (bool) {
	    //(y^2 == x^3 + 3) % p
	    uint p = P;
	    uint left = mulmod(point.y, point.y, p);
	    uint right = addmod(mulmod(mulmod(point.x, point.x, p), point.x, p), 3, p);
	    
	    return (left == right);
	}
	
	function Equals(Data memory A, Data memory B) public pure returns (bool) {
	    return ((A.x == B.x) && (A.y == B.y));
	}
	
	function Negate(Data memory point) public pure returns (Data memory) {
	    return Data(point.x, P - (point.y % P));
	}
	
	function Add(Data memory A, Data memory B) public view returns (Data memory C)	{
	    uint[] memory data = new uint[](4);
	    data[0] = A.x;
	    data[1] = A.y;
	    data[2] = B.x;
	    data[3] = B.y;
	    
	    assembly {
	        //Call ECAdd
        	let success := staticcall(sub(gas, 2000), 0x06, add(data, 0x20), 0x80, add(data, 0x20), 0x40)
       	 
        	// Use "invalid" to make gas estimation work
         	switch success case 0 { revert(data, 0x80) }
	    }
	    
	    C = Data(data[0], data[1]);
	}
	
	function Multiply(Data memory A, uint s) public view returns (Data memory C) {
	    uint[] memory data = new uint[](3);
	    data[0] = A.x;
	    data[1] = A.y;
	    data[2] = s;
	    
	    assembly {
	        //Call ECAdd
        	let success := staticcall(sub(gas, 2000), 0x07, add(data, 0x20), 0x60, add(data, 0x20), 0x40)
       	 
        	// Use "invalid" to make gas estimation work
         	switch success case 0 { revert(data, 0x80) }
	    }
	    
	    C = Data(data[0], data[1]);
	}

    function HashToScalar(Data memory A) public pure returns (uint) {
        return uint(keccak256(abi.encodePacked(A.x, A.y)));
    }
    
    function HashToPoint(Data memory A) public view returns (Data memory) {
        return FromX(HashToScalar(A));
    }
}