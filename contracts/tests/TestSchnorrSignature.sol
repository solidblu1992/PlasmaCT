pragma solidity ^0.5.0;

import "./SchnorrSignature.sol";

contract TestSchnorrSignature {
    using G1Point for G1Point.Data;
    using SchnorrSignature for SchnorrSignature.Data;
    
    constructor() public {}
    function Kill() public { selfdestruct(msg.sender); }
    
    function Recover() public view returns (bytes memory pub_key) {
        SchnorrSignature.Data memory sig = SchnorrSignature.Data(
            G1Point.Data(   0x1a0fc7c4d0b4398ab54c7de5b468346e99ca4d1d0900ee87a42d309720b047b2,
                            0x2ff799ef82792aac086dfc8d7d548589d44d34230e09e2b5654d91bd53a55ebd),
            0x9fc80c58c187361ca2ccdfb97315f55985b53a09fb2ddd91e84330a12ccc5e6,
            "Hello World"
        );
        
        //Should recover to:
        //0x13e9edf759f89b5cdd2d491d3d21a6bdaaede22254778e108fbdd2c9a472c34f033ce1f1f68ef44b85f2824b19da6ecd12efa1f2ba6c23d45adedccd81b111b4
    
        pub_key = sig.Recover().Serialize();
    }
    
    function Serialize(uint x, uint y, uint s, string memory message) public pure returns (bytes memory sig_bytes) {
        return SchnorrSignature.Serialize(SchnorrSignature.Data(G1Point.Data(x, y), s, message));
    }
    
    function Deserialize(bytes memory sig_bytes) public pure returns (uint x, uint y, uint s, string memory message) {
        SchnorrSignature.Data memory sig = SchnorrSignature.Deserialize(sig_bytes);
        x = sig.R.x;
        y = sig.R.y;
        s = sig.s;
        message = sig.message;
    }
}