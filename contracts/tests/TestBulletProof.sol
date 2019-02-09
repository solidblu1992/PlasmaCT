pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./BulletProof.sol";

contract TestBulletProof {
    using G1Point for G1Point.Data;
    using BulletProof for BulletProof.Data;
    
    constructor() public {}
    
    function DebugKill() public { selfdestruct(msg.sender); }
    
    function keccak_256(bytes memory b) public returns (bytes32) {
        return keccak256(abi.encodePacked(b));
    }
    
    function DeserializeMultiple(bytes memory b)
        public pure returns (G1Point.Data[] memory p)
    {
        p = G1Point.DeserializeMultiple(b);
    }
    
    function DeserializeMultipleGT(bytes memory b)
        public returns (G1Point.Data[] memory p)
    {
        p = G1Point.DeserializeMultiple(b);
    }
    
    function VerifyGiHiMerkelLeaf(bytes memory leaf_bytes, uint8 chunk_index, bytes32 level2_hash, bytes32 level1hash) public pure returns (bool) {
        return BulletProof.VerifyGiHiMerkelLeaf(leaf_bytes, chunk_index, level2_hash, level1hash);
    }
}