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
	
	function GetG1() public pure returns (Data memory G1) {
	    G1 = Data(1, 2);
	}
	
	function GetH() public pure returns (Data memory H) {
	    //H = HashToPoint(GetG1());
	    H = Data(   0x277a420332215ead37ba61fee84f0d216a345e762af8efd15453697170b3cdc5,
	                0x1b312cd37d4ad474fc299c9689fc0f347a2ec2b5b474a41b343142ee5fdd097a  );
	}
	
	
	
	///Base Functions
	//Get G1Point from desired x coordinate (increment x if not on curve)
	function FromX(uint x) public view returns (Data memory) {
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
	function IsOnCurve(Data memory point) public pure returns (bool) {
	    //(y^2 == x^3 + 3) % p
	    uint p = P;
	    uint left = mulmod(point.y, point.y, p);
	    uint right = addmod(mulmod(mulmod(point.x, point.x, p), point.x, p), 3, p);
	    
	    return (left == right);
	}
	
	//Check to see if both G1Points are equal
	function Equals(Data memory A, Data memory B) public pure returns (bool) {
	    return ((A.x == B.x) && (A.y == B.y));
	}
	
	//Negates the G1 Point
	function Negate(Data memory point) public pure returns (Data memory) {
	    return Data(point.x, P - (point.y % P));
	}
	
	//Calculates G1 Point addition using precompile
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
	
	//Calculates G1 Point scalar multiplication using precompile
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

    //Calculates the keccak256 hash of a G1 Point
    function HashToScalar(Data memory A) public pure returns (uint) {
        return uint(keccak256(abi.encodePacked(A.x, A.y)));
    }
    
    //Uses the keccak256 hash of a G1 Point to generate a new point (e.g. H = HashToPoint(G1))
    function HashToPoint(Data memory A) public view returns (Data memory) {
        return FromX(HashToScalar(A));
    }



    ///Helper functions to save calls to library
    //Saves a call to GetG1() or GetH()
    function MultiplyG1(uint s) public view returns (Data memory) {
        return Multiply(GetG1(), s);
    } 
    
    function MultiplyH(uint s) public view returns (Data memory) {
        return Multiply(GetH(), s);
    }
    
    //Calculates a*A + b*B
    function Shamir(Data memory A, Data memory B, uint a, uint b) public view returns (Data memory) {
        return Add(Multiply(A, a), Multiply(B, b));
    }
    
    //Calculates g*G1 + h*H
    function CalcPedersen(uint g, uint h) public view returns (Data memory) {
        return Add(Multiply(GetG1(), g), Multiply(GetH(), h));
    }

    //Calculates a*A + b*B + c*C + ...
    function MultiExp(Data[] memory points, uint[] memory s) public view returns (Data memory point) {
        require(points.length > 0);
        require(points.length == s.length);
        
        point = Multiply(points[0], s[0]);
        
        for (uint i = 1; i < s.length; i++) {
            point = Add(point, Multiply(points[i], s[i]));
        }
    }

    //Given an array of points (A, B, C, D, ...), double and add points (e.g. ((A*2 + B)*2 + C)*2 + D ...)
    function DoubleAndAdd(Data[] memory points) public view returns (Data memory point) {
        point = points[0];
        for (uint i = 1; i < points.length; i++) {
            point = Add(point, point);      //Double
            point = Add(point, points[i]);  //Add
        }
    }
}