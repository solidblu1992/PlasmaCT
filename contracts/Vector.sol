pragma solidity ^0.5.0;

import "./Scalar.sol";

library Vector {
    uint private constant modulo = 0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001;
    
    //Create vector = v^0, v^1, v^2, ..., v^(lenght-1)
	function Powers(uint v, uint length) internal pure returns (uint[] memory vec) {
	    require(length > 0);
	    
	    vec = new uint[](length);
	    vec[0] = 1;
	    
	    for (uint i = 1; i < length; i++) {
	        vec[i] = mulmod(vec[i-1], v, modulo);
	    }
    }
    
    //Get sum of vector
    function Sum(uint[] memory vec) internal pure returns (uint sum) {
        for (uint i = 0; i < vec.length; i++) {
            sum = addmod(sum, vec[i], modulo);
        }
    }
    
    //Get inner product
    function InnerProduct(uint[] memory a, uint[] memory b) internal pure returns (uint[] memory c) {
        require(a.length == b.length);
        c = new uint[](a.length);
        
        for (uint i = 0; i < a.length; i++) {
            c[i] = mulmod(a[i], b[i], modulo);
        }
    }
    
    //Get dot product
    function Dot(uint[] memory a, uint[] memory b) internal pure returns (uint dot) {
        require(a.length == b.length);
        
        for (uint i = 0; i < a.length; i++) {
            if (dot == 0) {
                dot = mulmod(a[i], b[i], modulo);
            }
            else {
                dot = addmod(dot, mulmod(a[i], b[i], modulo), modulo);
            }
        }
    }
    
    //Get vector slice
    function Slice(uint[] memory vec, uint start, uint length) internal pure returns (uint[] memory slice) {
        require(start < vec.length);
        require((start + length) < vec.length);
        
        slice = new uint[](length);
        for (uint i = 0; i < length; i++) {
            slice[i] = vec[i + start];
        }
    }
    
    //Calculate inverse of each scalar in vector
    function Inverse(uint[] memory a) internal pure returns (uint[] memory out) {
        uint[] memory intermediates = new uint[](a.length);
        out = new uint[](a.length);
        
        //Calculate products: a, a*b, a*b*c, ...
        intermediates[0] = a[0];
        for (uint i = 1; i < a.length; i++) {
            intermediates[i] = mulmod(intermediates[i-1], a[i], modulo);
        }
        
        //Perform one inverse
        uint index = a.length-1;
        intermediates[index] = Scalar.Inverse(intermediates[index]);
        
        //Work backwards
        for (uint i = 0; i < (a.length-1); i++) {
            out[index] = mulmod(intermediates[index], intermediates[index-1], modulo); //e.g.    e = (1/abcde * abcd)
            intermediates[index-1] = mulmod(intermediates[index], a[index], modulo); //e.g. 1/abcd = (1/abcde * e)
            index--;
        }
        
        //Store last inverse
        out[0] = intermediates[0];
    }
}
