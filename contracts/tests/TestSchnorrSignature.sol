pragma solidity ^0.5.0;

import "./G1Point.sol";

contract TestSchnorrSignature {
    using G1Point for G1Point.Data;
    constructor() public {}
    function Kill() public { selfdestruct(msg.sender); }
    
    function Test() public pure returns (uint len, uint b1, uint b2) {
        G1Point.Data memory p = G1Point.Data(1, 2);
        bytes memory b = abi.encodePacked(p.x, p.y);
        
        len = b.length;
        
        assembly {
            b1 := mload(add(b, 32))
            b2 := mload(add(b, 64))
        }
    }
    
    function Add() public view returns (bytes memory out) {
        bytes memory g1 = "0x0000000000000000000000000000000000000000000000000000000000000001";
        G1Point.Data memory G1 = G1Point.Deserialize(g1);
        G1 = G1.Add(G1);
        out = G1.Serialize(true);
    }
    
    function Double(bytes memory b) public view returns (uint x, uint y, uint G1_x, uint G1_y) {
        G1Point.Data memory P = G1Point.Deserialize(b);
        P = P.Add(P);
        x = P.x;
        y = P.y;
        
        P = G1Point.MultiplyG1(2);
        G1_x = P.x;
        G1_y = P.y;
    }
}