pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

library G1Point {
	struct Data {
	    uint x;
	    uint y;
	}
	
	///Curve parameters and generators
	uint constant private N = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;
	uint constant private P = 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;
	
	///MSB used for point compression and expansion
	uint constant private sign_flag = 0x8000000000000000000000000000000000000000000000000000000000000000;
	
	//alt_bn_128 curve order
	function GetN() internal pure returns (uint) {
	    return N;
	}
	
	//alt_bn_128 field modulus
	function GetP() internal pure returns (uint) {
	    return P;
	}
	
	//Zero Point
	function GetZeroPoint() internal pure returns (Data memory Zero) {
	    Zero = Data(0, 0);
	}
	
	//alt_bn_128 Generator Point
	function GetG1() internal pure returns (Data memory G1) {
	    G1 = Data(1, 2);
	}
	
	//2nd Generator point where gamma is unknown for the equation: H = gammma*G1
	function GetH() internal pure returns (Data memory H) {
	    //H = HashToPoint(GetG1());
	    H = Data(   0x2854ddec56b97fb3a6d501b8a6ff07891ce7aeb22c1cc74cf0a18ebc3f15220b,
	                0x23a967b0d240d4264fea929d6a02ba4b7c612c0a4ef611e92eb011aa854cdbf7  );
	}
	
	//Special Generator Points used for Bullet Proofs
	function GetGi(uint i) internal view returns (Data memory Gi) {
	    return FromX(uint(keccak256(abi.encodePacked("Gi", i))));
	}
	
	function GetHi(uint i) internal view returns (Data memory Gi) {
	    return FromX(uint(keccak256(abi.encodePacked("Hi", i))));
	}
	
	///Base Functions
	//Get G1Point from desired x coordinate (increment x if not on curve)
	function FromX(uint x) internal view returns (Data memory) {
	    uint p = P;
	    x = x % p;
	    
	    uint[] memory data = new uint[](6);
	    data[0] = 0x20;
	    data[1] = 0x20;
	    data[2] = 0x20;
	    //data[3] = 0;
	    data[4] = 0xc19139cb84c680a6e14116da060561765e05aa45a1c72a34f082305b61f3f52;  // (p+1)/4
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
	
	//Check to see if G1Point is on curve
	function IsOnCurve(Data memory point) internal pure returns (bool) {
	    //(y^2 == x^3 + 3) % p
	    uint p = P;
	    uint left = mulmod(point.y, point.y, p);
	    uint right = addmod(mulmod(mulmod(point.x, point.x, p), point.x, p), 3, p);
	    
	    return (left == right);
	}
	
	//Checks to see if point is zero
	function IsZero(Data memory point) internal pure returns (bool) {
	    return (point.x == 0 && point.y == 0);
	}
	
	//Check to see if both G1Points are equal
	function Equals(Data memory A, Data memory B) internal pure returns (bool) {
	    return ((A.x == B.x) && (A.y == B.y));
	}
	
	//Negates the G1 Point
	function Negate(Data memory point) internal pure returns (Data memory) {
	    return Data(point.x, P - (point.y % P));
	}
	
	//Calculates G1 Point addition using precompile
	function Add(Data memory A, Data memory B) internal view returns (Data memory C)	{
	    //Trivial Cases, no precompile call required
	    if (IsZero(A)) return B;
	    if (IsZero(B)) return A;
	    
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
	
	//Point Subraction
	function Subtract(Data memory A, Data memory B) internal view returns (Data memory C)	{
	    return Add(A, Negate(B));
	}
	
	//Calculates G1 Point scalar multiplication using precompile
	function Multiply(Data memory A, uint s) internal view returns (Data memory C) {
	    //Trivial Cases
	    if (IsZero(A) || s == 1) return A;
	    if (s == 0) return GetZeroPoint();
	    
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

    ///Point Compression
    function CompressPoint(Data memory A) internal pure returns (uint compressed_point) {
        compressed_point = A.x;
        
        if (A.y & 1 != 0) {
            compressed_point |= sign_flag;
        }
    }
    
    function ExpandPoint(uint compressed_point) internal view returns (Data memory A) {
        //Check bit flag
        bool odd = (compressed_point & sign_flag != 0);
        
        //Remove bit flag
        if (odd) {
            compressed_point &= ~sign_flag;
        }
        
        //Get y-coord
        A = FromX(compressed_point);
        
        //Check sign, correct if necessary
        if (odd) {
            if (A.y & 1 == 0) {
                A.y = P - A.y;
            }
        }
        else {
            if (A.y & 1 == 1) {
                A.y = P - A.y;
            }
        }
    }

    ///Hash Functions
    //Calculates the keccak256 hash of a G1 Point
    function HashToScalar(Data memory A) internal pure returns (uint) {
        return uint(keccak256(abi.encodePacked(A.x, A.y, "G1")));
    }
    
    //Uses the keccak256 hash of a G1 Point to generate a new point (e.g. H = HashToPoint(G1))
    function HashToPoint(Data memory A) internal view returns (Data memory) {
        return FromX(HashToScalar(A));
    }

	//Uses the keccak256 hash of an address to generate a new point
	function HashAddressToPoint(address addr) internal view returns (Data memory) {
		return FromX(uint(keccak256(abi.encodePacked(addr))));
	}

    ///Helper functions to save calls to library
    //Saves a call to GetG1() or GetH()
    function MultiplyG1(uint s) internal view returns (Data memory) {
        return Multiply(GetG1(), s);
    } 
    
    function MultiplyH(uint s) internal view returns (Data memory) {
        return Multiply(GetH(), s);
    }
    
    function PointArrayToUintArray(Data[] memory points) internal pure returns (uint[] memory coords) {
        coords = new uint[](points.length*2);
        for (uint i = 0; i < points.length; i++) {
            coords[2*i] = points[i].x;
            coords[2*i+1] = points[i].y;
        }
    }
    
    //Calculates a*A + b*B
    function Shamir(Data memory A, Data memory B, uint a, uint b) internal view returns (Data memory) {
        return Add(Multiply(A, a), Multiply(B, b));
    }
    
    //Calculates g*G1 + h*H
    function CalcPedersen(uint g, uint h) internal view returns (Data memory) {
        return Add(Multiply(GetG1(), g), Multiply(GetH(), h));
    }

    //Calculates a*A + b*B + c*C + ...
    function MultiExp(Data[] memory points, uint[] memory s) internal view returns (Data memory point) {
        require(points.length > 0);
        require(points.length == s.length);
        
        point = Multiply(points[0], s[0]);
        
        for (uint i = 1; i < s.length; i++) {
            point = Add(point, Multiply(points[i], s[i]));
        }
    }

    //Given an array of points (A, B, C, D, ...), double and add points (e.g. ((A*2 + B)*2 + C)*2 + D ...)
    function DoubleAndAdd(Data[] memory points) internal view returns (Data memory point) {
        point = points[0];
        for (uint i = 1; i < points.length; i++) {
            point = Add(point, point);      //Double
            point = Add(point, points[i]);  //Add
        }
    }
    
    //Serializes G1Point into bytes
    function Serialize(Data memory point) internal pure returns (bytes memory b) {
        //Pack uncompressed point
        b = abi.encodePacked(point.x, point.y);
    }
    
    //Deserialize G1Point from bytes
    function Deserialize(bytes memory b) internal pure returns (Data memory point) {
        //Fetch uncompressed point
        uint temp;
        assembly { temp := mload(add(b, 32)) }
        point.x = temp;
        
        assembly { temp := mload(add(b, 64)) }
        point.y = temp;
    }
    
    function DeserializeMultiple(bytes memory b) internal pure returns (Data[] memory point) {
        //Check input
        require(b.length % 64 == 0);
        
        //Fetch points
        point = new Data[](b.length / 64);
        
        for (uint i = 0; i < point.length; i++) {
            uint ptr = 32 + i*64;
            
            uint temp;
            assembly { temp := mload(add(b, ptr)) }
            point[i].x = temp;
            
            assembly { temp := mload(add(add(b, ptr), 32)) }
            point[i].y = temp;
        }
    }
}
