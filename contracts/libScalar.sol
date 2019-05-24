pragma solidity ^0.5.0;

library Scalar {
    uint private constant modulo = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;

    function Negate(uint a) internal pure returns (uint) {
        if (a >= modulo) a = a % modulo;
        return (modulo - a);
    }
    
    function Square(uint a) internal pure returns (uint) {
        return mulmod(a, a, modulo);
    }

    function Add(uint a, uint b) internal pure returns (uint) {
        return addmod(a, b, modulo);
    }
    
    function Subtract(uint a, uint b) internal pure returns (uint) {
        return Add(a, Negate(b));
    }
    
    function Multiply(uint a, uint b) internal pure returns (uint) {
        return mulmod(a, b, modulo);
    }
    
    function Power(uint a, uint p) internal pure returns (uint power) {
        //Trivial Case
        if (p == 0) {
            power = 1;
        }
        //Identity
        else if (p == 1) {
            power = a;
        }
        //Square
        else if (p == 2) {
            power = Square(a);
        }
        //Low Powers
        else if (p < 16) {
            power = a;
            for (uint i = 0; i < p; i++) {
                power = mulmod(power, a, modulo);
            }
        }
        //Multiply and Add
        else {
            uint msb = 0x8000000000000000000000000000000000000000000000000000000000000000;
            uint bit;
            while (msb > 0) {
                bit = p & msb;
                
                //Add
                if (bit > 0) {
                    power = addmod(power, a, modulo);
                }
                
                //Double (Square)
                if (power > 0) {
                    power = mulmod(power, power, modulo);
                }
                
                msb >>= 1;
            }
        }
    }

	///Note: This function borrowed from androlo/standard-contracts/ECCMath.sol, modified slightly
	//Original Author: Andreas Olofsson (androlo1980@gmail.com)
	//Original Source: https://github.com/androlo/standard-contracts/blob/master/contracts/src/crypto/ECCMath.sol
	function Inverse(uint a) internal pure returns (uint) {
        if (a == 0 || a == modulo) revert();
        if (a > modulo) a = a % modulo;
        
        int t1;
        int t2 = 1;
        uint r1 = modulo;
        uint r2 = a;
        uint q;
        
        while (r2 != 0) {
            q = r1 / r2;
            (t1, t2, r1, r2) = (t2, t1 - int(q) * t2, r2, r1 - q * r2);
        }
        
        if (t1 < 0) return (modulo - uint(-t1));
        
        return uint(t1);
    }
}