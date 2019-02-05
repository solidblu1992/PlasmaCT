pragma solidity ^0.5.0;

import "github.com/OpenZeppelin/openzeppelin-solidity/contracts/token/ERC20/ERC20.sol";

//Generic ERC20, mintable by everyone, can be destroyed by owner 
contract TestERC20 is ERC20 {
    address debug_owner;
    
    constructor() ERC20() public {
        debug_owner = msg.sender;
    }
    function DebugKill() public {
        require(debug_owner == address(0x0) || debug_owner == msg.sender);
        selfdestruct(msg.sender);
    }
    
    //Allow minting of tokens for everyone
    function Mint(address account, uint amount) public {
        _mint(account, amount);
    }
}