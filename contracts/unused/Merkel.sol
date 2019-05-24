pragma solidity ^0.5.0;

library Merkel {
    function Create(bytes32[] memory a, uint start, uint length)
        internal pure returns (bytes32)
    {
        //Input checks
        require(length > 0);
        require(start < a.length);
        require(length <= a.length);
        require((start+length) <= a.length);
        
        //Copy a into m
        bytes32[] memory m = new bytes32[](length);
        for (uint i = 0; i < length; i++) {
            m[i] = a[start+i];
        }
        
        //Find merkel root
        uint l_prime = m.length;
        
        while (l_prime > 0) {
            uint l_prime_over_2 = l_prime >> 1;
            for (uint i = 0; i < l_prime_over_2; i++) {
                //If odd number at current level, need to hash 3 on last iteration
                if ((l_prime & 1 == 1) && (i == (l_prime_over_2-1))) {
                    m[i] = keccak256(abi.encodePacked(m[2*i], m[2*i+1], m[2*i+2])); 
                }
                //Normal case: hash 2
                else {
                    m[i] = keccak256(abi.encodePacked(m[2*i], m[2*i+1])); 
                }
            }
            
            l_prime >>= 1;
        }
        
        return m[0];
    }
    
    function CreateRecursive(bytes32[] memory a, uint start, uint length)
        internal pure returns (bytes32)
    {
        //Input checks
        require(length > 0);
        require(start < a.length);
        require(length <= a.length);
        require((start+length) <= a.length);
        
        if (length == 1) return keccak256(abi.encodePacked(a[start]));
        if (length == 2) return keccak256(abi.encodePacked(a[start], a[start+1]));
        if (length == 3) return keccak256(abi.encodePacked(a[start], a[start+1], a[start+2]));
        
        //Even Recursion
        uint length_over_2 = length / 2;
        return  keccak256(
                    abi.encodePacked(
                        CreateRecursive(a, start, length_over_2),
                        CreateRecursive(a, start+length_over_2, length_over_2 + (length & 1 == 0 ? 0 : 1))
                    )
                );
    }
}

contract MerkelTest {
    constructor() public {}
    
    function Kill() public { selfdestruct(msg.sender); }
    
    function Echo() public pure returns (bool) { return true; }

    function Merkelize(uint[] memory input, uint start, uint length)
        public pure returns (bytes32 out)
    {
        bytes32[] memory a = new bytes32[](input.length);
        for (uint i = 0; i < a.length; i++) {
            a[i] = keccak256(abi.encodePacked(input[i]));
        }
        
        out = Merkel.Create(a, start, length);
    }
    
    function MerkelizeRecursive(uint[] memory input, uint start, uint length)
        public pure returns (bytes32 out)
    {
        bytes32[] memory a = new bytes32[](input.length);
        for (uint i = 0; i < a.length; i++) {
            a[i] = keccak256(abi.encodePacked(input[i]));
        }
        
        out = Merkel.CreateRecursive(a, start, length);
    }
    
    function GasTest(uint[] memory input, uint start, uint length)
        public returns (bytes32 out)
    {
        out = Merkelize(input, start, length);
    }
    
    function GasTestRecursive(uint[] memory input, uint start, uint length)
        public returns (bytes32 out)
    {
        out = MerkelizeRecursive(input, start, length);
    }
}
