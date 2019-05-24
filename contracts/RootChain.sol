pragma solidity ^0.5.1;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";
import "./SchnorrSignature.sol";

contract RootChain {
    constructor() public {}
    function Kill() public { selfdestruct(msg.sender); }
    
    using G1Point for G1Point.Data;
    using SchnorrSignature for SchnorrSignature.Data;
    
    event NewDepositBlock
    (
        uint indexed blk_num,
        uint new_input
    );
    
    uint public block_count;
    mapping (uint => bytes32) public blocks;
    
    function Deposit(G1Point.Data memory BF, SchnorrSignature.Data memory sig) public payable {
        require(msg.value > 1 szabo);
        require(BF.IsOnCurve());
        require(sig.Recover().Equals(BF));
        
        G1Point.Data memory Input = BF.Add(G1Point.MultiplyH(msg.value));
        
        //Emit Log
        emit NewDepositBlock(block_count, Input.CompressPoint());
        
        //Store Block
        blocks[block_count] = keccak256(abi.encodePacked(block_count, Input.x, Input.y));
        block_count++;
    }
}