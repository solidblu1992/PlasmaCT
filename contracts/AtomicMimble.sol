pragma solidity ^0.4.24;

library Secp256k1 {
	uint public constant Ncurve = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141;
	uint public constant Pcurve = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f;
	uint public constant Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798;
	uint public constant Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8;
	uint8 public constant Gy_parity = 0x2;
	
	//Popular functions
	function GetG() public pure returns (uint[2] G) {
	    (G[0], G[1]) = (Gx, Gy);
	}
	
	function GetP() public pure returns (uint) {
	    return Pcurve;
	}
	
	function GetN() public pure returns(uint) {
	    return Ncurve;
	}
	
	function Negate(uint[2] P) public pure returns (uint[2] Q) {
	    (Q[0], Q[1]) = (P[0], Ncurve - P[1] % Ncurve);
	}
	
	function Add(uint[2] P, uint[2] Q) public pure returns (uint[2] R) {
	    uint[3] memory R3 = Add3([P[0], P[1], 1], [Q[0], Q[1], 1]);
	    R = Normalize3(R3);
	}
	
	function Subtract(uint[2] P, uint[2] Q) public pure returns (uint[2] R) {
	    return Add(P, Negate(Q));   
	}
	
	function Multiply(uint[2] P, uint k, uint[2] W) public pure returns (bool) {
	    return Multiply_Compressed(GetYParity(P[1]), P[0], k, W);
	}
	
	function MultiplyG(uint k, uint[2] W) public pure returns (bool) {
	    return Multiply_Compressed(Gy_parity, Gx, k, W);
	}
	
	function ModInvP(uint a) public pure returns (uint) {
        return ModInv(a, Pcurve);    
    }
    
    function ModInvN(uint a) public pure returns (uint) {
        return ModInv(a, Ncurve);    
    }
	
	//Less-Popular / internal use functions
	function GetG_Compressed() public pure returns (uint8, uint) {
		return (Gy_parity, Gx);
	}
	
	function GetYParity(uint Py) public pure returns (uint8) {
	    if (Py & 0x1 == 0) {
	        return 0x2;
	    }
	    else {
	        return 0x3;
	    }
	}
	
	function Negate3(uint[3] P) public pure returns (uint256[3] Q) {
	    (Q[0], Q[1], Q[2]) = (P[0], Ncurve - (P[1] % Ncurve), P[2]);
	}
	
	function Double3(uint[3] P) public pure returns (uint[3] Q) {
	    uint p = Pcurve;
        if (P[2] == 0)
            return;
        uint Px = P[0];
        uint Py = P[1];
        uint Py2 = mulmod(Py, Py, p);
        uint s = mulmod(4, mulmod(Px, Py2, p), p);
        uint m = mulmod(3, mulmod(Px, Px, p), p);
        uint Qx = addmod(mulmod(m, m, p), p - addmod(s, s, p), p);
        Q[0] = Qx;
        Q[1] = addmod(mulmod(m, addmod(s, p - Qx, p), p), p - mulmod(8, mulmod(Py2, Py2, p), p), p);
        Q[2] = mulmod(2, mulmod(Py, P[2], p), p);
	}
	
	function Add3(uint[3] P, uint[3] Q) public pure returns (uint[3] R) {
	    if(P[2] == 0)
            return Q;
        if(Q[2] == 0)
            return P;
        uint p = Pcurve;
        uint[4] memory zs; // Pz^2, Pz^3, Qz^2, Qz^3
        zs[0] = mulmod(P[2], P[2], p);
        zs[1] = mulmod(P[2], zs[0], p);
        zs[2] = mulmod(Q[2], Q[2], p);
        zs[3] = mulmod(Q[2], zs[2], p);
        uint[4] memory us = [
            mulmod(P[0], zs[2], p),
            mulmod(P[1], zs[3], p),
            mulmod(Q[0], zs[0], p),
            mulmod(Q[1], zs[1], p)
        ]; // Pu, Ps, Qu, Qs
        if (us[0] == us[2]) {
            if (us[1] != us[3])
                return;
            else {
                return Double3(P);
            }
        }
        uint h = addmod(us[2], p - us[0], p);
        uint r = addmod(us[3], p - us[1], p);
        uint h2 = mulmod(h, h, p);
        uint h3 = mulmod(h2, h, p);
        uint Rx = addmod(mulmod(r, r, p), p - h3, p);
        Rx = addmod(Rx, p - mulmod(2, mulmod(us[0], h2, p), p), p);
        R[0] = Rx;
        R[1] = mulmod(r, addmod(mulmod(us[0], h2, p), p - Rx, p), p);
        R[1] = addmod(R[1], p - mulmod(us[1], h3, p), p);
        R[2] = mulmod(h, mulmod(P[2], Q[2], p), p);
	}
	
	function Subtract3(uint[3] P, uint[3] Q) public pure returns (uint[3] R) {
	    return Add3(P, Negate3(Q));
	}
    
    function ModInv(uint a, uint p) public pure returns (uint) {
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
    
    function Normalize3(uint[3] P3) public pure returns (uint[2] P) {
        if (P3[2] == 1) {
            (P[0], P[1]) = (P3[0], P3[1]);
        }
        else {
            uint p = Pcurve;
            uint z_inv = ModInv(P3[2], p);
            (P[0], P[1]) = (mulmod(P3[0], z_inv, p), mulmod(P3[1], z_inv, p));
        }
    }

    function Multiply_Compressed(uint8 Py_parity, uint Px, uint k, uint[2] W) public pure returns (bool) {
        address kP_hash = ecrecover(0, (Py_parity + 25), bytes32(Px), bytes32(mulmod(Px, k, Ncurve)));
	    return (kP_hash == address(keccak256(abi.encodePacked(W[0], W[1]))));
	}
}

library Schnorr {
    function recover(bytes message, uint[2] R, uint s, uint[2] W_sG, uint[2] W_P)
        public pure returns (bool)
    {
        uint e = uint(keccak256(abi.encodePacked(message, R[0], R[1])));
        uint e_inv = Secp256k1.ModInvN(e);
        
        //P = e_inv*(R - sG)
        //"Compute" sG
        if (!Secp256k1.MultiplyG(s, W_sG)) return false;
        if (!Secp256k1.Multiply(Secp256k1.Subtract(R, W_sG), e_inv, W_P)) return false;
        
        return true;
    }
    
    function recover_multiple(bytes message, uint[] R, uint[] s, uint[] W_eR, uint[2] W_s_sumG) 
        public pure returns (uint[2] P)
    {
        //Check array lengths
        require(R.length % 2 == 0);
        require(R.length / 2 == s.length);
        require(R.length == W_eR.length);
        
        //Recover points
        uint[3] memory P3;
        uint s_sum;
        uint e_inv;
        uint n = Secp256k1.GetN();
        
        for (uint i = 0; i < s.length; i++) {
            e_inv = Secp256k1.ModInvN(uint(keccak256(abi.encodePacked(message, R[2*i], R[2*i+1]))));
            
            //s_sum = e_inv[0]*s[0] + ... + e_inv[N-1]*s[N-1]
            s_sum = addmod(s_sum, mulmod(e_inv, s[i], n), n);
            
            //P = e_inv[0]*R[0] + ... + e_inv[N-1]*R[N-1]
            if (!Secp256k1.Multiply([R[2*i], R[2*i+1]], e_inv, [W_eR[2*i], W_eR[2*i+1]])) revert();
            if (i == 0) {
                (P[0], P[1]) = (W_eR[2*i], W_eR[2*i+1]);
            }
            else {
                P3 = Secp256k1.Add3(P3, [W_eR[2*i], W_eR[2*i+1], 1]);
            }
        }
        
        //P = sum(e_inv*R) - sum(e_inv*s)*G
        if (!Secp256k1.MultiplyG(s_sum, W_s_sumG)) revert();
        P3 = Secp256k1.Subtract3(P3, [W_s_sumG[0], W_s_sumG[1], 1]);
        P = Secp256k1.Normalize3(P3);
    }
}

contract AtomicMimble {
	function kill() public {
	   selfdestruct(msg.sender);
	}
	
	function SchnorrTest(bytes message, uint[2] R, uint s, uint[2] W_sG, uint[2] W_P)
        public pure returns (bool)
    {
        return Schnorr.recover(message, R, s, W_sG, W_P);      
    }
    
    function SchnorrGasTest(bytes message, uint[2] R, uint s, uint[2] W_sG, uint[2] W_P)
        public returns (bool)
    {
        return Schnorr.recover(message, R, s, W_sG, W_P);      
    }
}