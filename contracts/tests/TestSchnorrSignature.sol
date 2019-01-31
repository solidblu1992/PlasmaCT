pragma solidity ^0.5.0;

import "./SchnorrSignature.sol";

contract TestSchnorrSignature {
    using G1Point for G1Point.Data;
    using SchnorrSignature for SchnorrSignature.Data;
    
    constructor() public {}
    function Kill() public { selfdestruct(msg.sender); }
    
    function Recover() public view returns (bytes memory pub_key) {
        SchnorrSignature.Data memory sig = SchnorrSignature.Data(
            "Hello World",
            G1Point.Data(   0x1a0fc7c4d0b4398ab54c7de5b468346e99ca4d1d0900ee87a42d309720b047b2,
                            0x2ff799ef82792aac086dfc8d7d548589d44d34230e09e2b5654d91bd53a55ebd),
            0x9fc80c58c187361ca2ccdfb97315f55985b53a09fb2ddd91e84330a12ccc5e6
        );
    
        pub_key = sig.Recover().Serialize(false);
    }
}