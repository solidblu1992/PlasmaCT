pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./RingSignature.sol";
import "./DAIInterface.sol";

contract BondedRingSignature {    
	constructor(RingSignature.Data memory sig) public {
		uint bond_amount = 
		uint finalizationBlock = block.number + 40000;
	    ERC20 DAI = ERC20(0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359);
	}
	
	function Fund() public {
		DAI.transferFrom(msg.sender, address(this), 1000);
	}
}