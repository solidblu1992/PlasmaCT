pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;

contract Debuggable {
    address owner;
    constructor() public {
        owner = msg.sender;
    }
    
    function kill() public {
        if (owner == msg.sender || owner == 0) {
            selfdestruct(msg.sender);
        }
    }
}

contract ScalarMath is Debuggable {
	constructor() public {}
	
	function ModInv(uint a, uint p) public constant returns (uint) {
		if (a == 0 || a == p || p == 0)
			revert();
        if (a > p)
            a = a % p;
        int t1;
        int t2 = 1;
        uint r1 = p;
        uint r2 = a;
        uint q;
        while (r2 != 0) {
            q = r1 / r2;
            (t1, t2, r1, r2) = (t2, t1 - int(q) * t2, r2, r1 - q * r2);
        }
        if (t1 < 0)
            return (p - uint(-t1));
        return uint(t1);
    }

	function MontgomeryBatchInversion(uint[] a, uint p) public constant returns (uint[] a_inv) {
		//Allocate Arrays
		a_inv = new uint[](a.length);
		uint[] memory intermediate = new uint[](a.length);
		
		//Fill intermediate slots: a, ab, abc, ..., abc...n
		intermediate[0] = a[0];
		
		uint i;
		for (i = 1; i < a.length; i++) {
			intermediate[i] = mulmod(intermediate[i-1], a[i], p);
		}
		
		//Calculate single mod inverse
		uint working = ModInv(intermediate[a.length-1], p);
		
		//Calculate the rest of the inverses
		for (i = (a.length-1); i > 0; i--) {
			a_inv[i] = mulmod(working, intermediate[i-1], p);
			working = mulmod(working, a[i], p);
		}
		
		//Store last inverse
		a_inv[0] = working;
	}
}

contract ECMath is ScalarMath {
    constructor() public {}
    
    //Generators and Constants
    struct G1Point {
        uint x;
        uint y;
    }
    
    struct G2Point {
        uint[2] x;
        uint[2] y;
    }
    
    function GetG1() public pure returns (G1Point) {
        return G1Point(1, 2);
    }
    
    function GetG2() public pure returns (G2Point) {
        return G2Point(
			[11559732032986387107991004021392285783925812861821192530917403151452391805634,
			 10857046999023057135944570762232829481370756359578518086990519993285655852781],
			[4082367875863433681332203403145435568316851327593401208105741076214120093531,
			 8495653923123431417604973247489272438418190587263600148770280649306958101930]
		);
    }
    
    function GetFieldModulus() public pure returns (uint) {
        return 0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47;
    }
    
    function GetCurveOrder() public pure returns (uint) {
        return 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;
    }
    
    //Basic Functions
    function IsZero(G1Point A) public pure returns (bool) {
        return (A.x == 0) && (A.y == 0);
    }
    
    function IsEqual(G1Point A, G1Point B) public pure returns (bool) {
        return (A.x == B.x) && (A.y == B.y);
    }
    
    function Negate(G1Point A) public pure returns (G1Point) {
        uint Pcurve = GetFieldModulus();
        return G1Point(A.x, Pcurve - (A.y % Pcurve));   
    }
    
    function ExpMod(uint base, uint exponent, uint modulus) public constant returns (uint) {
        uint[6] memory input = [0x20, 0x20, 0x20, base, exponent, modulus];
        uint[1] memory output;
        bool success;
        assembly {
            success := call(sub(gas, 2000), 5, 0, input, 0xC0, output, 0x20)
        }
        require(success);
        
        return output[0];
    }
    
    function Add(G1Point A, G1Point B) public constant returns (G1Point C) {
        uint[4] memory input = [A.x, A.y, B.x, B.y];
        bool success;
        assembly {
            success := call(sub(gas, 2000), 6, 0, input, 0xc0, C, 0x60)
        }
        require(success);
    }
    
	function Subtract(G1Point A, G1Point B) public constant returns (G1Point C) {
		return Add(A, Negate(B));
	}
	
    function Multiply(G1Point A, uint s) public constant returns (G1Point B) {
        uint[3] memory input = [A.x, A.y, s];
        bool success;
        assembly {
            success := call(sub(gas, 2000), 7, 0, input, 0x80, B, 0x60)
        }
        require(success);
    }

    function PairingCheck(G1Point[] P1, G2Point[] P2) public constant returns (bool success) {
        require(P1.length == P2.length);
        uint input_length = P1.length*6;
        uint[] memory input = new uint[](input_length);
        uint index = 0;
        for (uint i = 0; i < P1.length; i++) {
            input[index] = P1[i].x;
            input[index+1] = P1[i].y;
            input[index+2] = P2[i].x[0];
            input[index+3] = P2[i].x[1];
            input[index+4] = P2[i].y[0];
            input[index+5] = P2[i].y[1];
            index += 6;
        }
        
        uint[1] memory output;
        assembly {
            success := call(sub(gas, 2000), 8, 0, add(input, 0x20), mul(input_length, 0x20), output, 0x20)
        }
        require(success);
        return output[0] != 0;
    }

    function GetG1PointFromX(uint x) public constant returns (G1Point A) {
        uint a = 0xc19139cb84c680a6e14116da060561765e05aa45a1c72a34f082305b61f3f52; //(p+1)/4
        bool searching = true;
        uint Pcurve = GetFieldModulus();
        
        if (x >= Pcurve) {
            x = x % Pcurve;
        }
        
        uint y;
        while (searching) {
            uint y_squared = mulmod(x, x, Pcurve);
            y_squared = mulmod(y_squared, x, Pcurve);
            y_squared = addmod(y_squared, 3, Pcurve);
            
            y = ExpMod(y_squared, a, Pcurve);
            
            if (y_squared == mulmod(y, y, Pcurve)) {
                searching = false;
            }
            else {
                x = addmod(x, 1, Pcurve);
            }
        }
   	 
    	return G1Point(x, y);
    }

    //Point Hash Functions
    function HashUintToG1Point(uint x) public constant returns (G1Point) {
        uint h = uint(keccak256(abi.encodePacked(x)));
        return GetG1PointFromX(h);
    }

    //Signature Functions
	struct SchnorrSignature {
		string message;
		G1Point R;
		uint s;
    }
	
    struct BLSSignature {
        G1Point P;
        G2Point S;
        G2Point M;
    }
    
	function RecoverSchnorr(SchnorrSignature sig) public constant returns (G1Point P) {
		uint e_inv = ModInv(uint(keccak256(abi.encodePacked(sig.R.x, sig.R.y, sig.message))), GetCurveOrder());
		P = Multiply(Subtract(sig.R, Multiply(GetG1(), sig.s)), e_inv);
	}
	
	function BatchRecoverSchnorr(SchnorrSignature[] sig) public constant returns (G1Point P) {
	    //Fetch curve order
	    uint Ncurve = GetCurveOrder();
	    
	    //Calculate e inverses, using Montgomery Batch Inversion
	    uint[] memory e_inv = new uint[](sig.length);
	    uint i;
	    for (i = 0; i < sig.length; i++) {
	        //Calculate e's
	        e_inv[i] = uint(keccak256(abi.encodePacked(sig[i].R.x, sig[i].R.y, sig[i].message)));
	    }
	    e_inv = MontgomeryBatchInversion(e_inv, Ncurve);
	    
	    //Calculate sums of (R[i]*e_inv[i]) and (s[i]*e_inv[i])
	    uint s_sum = mulmod(sig[0].s, e_inv[0], Ncurve);
	    G1Point memory R_sum = Multiply(sig[0].R, e_inv[0]);
	    for (i = 1; i < sig.length; i++) {
	        s_sum = addmod(s_sum, mulmod(sig[i].s, e_inv[i], Ncurve), Ncurve);
	        R_sum = Add(R_sum, Multiply(sig[i].R, e_inv[i]));
	    }
	    
	    //Add in (-s_sum*G1)
	    P = Subtract(R_sum, Multiply(GetG1(), s_sum));
	}
	
	function VerifySchnorr(SchnorrSignature sig, G1Point P, uint t /*If not using scriptless scripts, leave t=0*/) public constant returns (bool) {
	    if (IsZero(sig.R) || IsZero(P)) return false;
	    
	    uint Ncurve = GetCurveOrder();
	    uint e = uint(keccak256(abi.encodePacked(sig.R.x, sig.R.y, sig.message))) % Ncurve;
	    G1Point memory ST = Multiply(GetG1(), addmod(sig.s, t, Ncurve));
	    G1Point memory R_check = Add(Multiply(P, e), ST);
	    return IsEqual(sig.R, R_check);
	}
	
    function VerifyBLS(BLSSignature sig) public constant returns (bool) {
        G1Point[] memory P1 = new G1Point[](2);
        G2Point[] memory P2 = new G2Point[](2);
        
        //Pairing Check: e(P, M) + e(-G1, S) = 0
        P1[0] = sig.P;              P2[0] = sig.M;
        P1[1] = Negate(GetG1());    P2[1] = sig.S;
        return PairingCheck(P1, P2);
    }
}