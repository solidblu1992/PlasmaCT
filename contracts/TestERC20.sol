pragma solidity ^0.5.0;

import "github.com/OpenZeppelin/openzeppelin-solidity/contracts/token/ERC20/ERC20.sol";

//Generic ERC20, mintable by everyone, can be destroyed by owner
//goerli:   0xea100Bec80418680e55D28b655da6CbEF427275f
//owner:    0x616837c633c543a6796c34b6607CC3b36e38fFAa
contract TestERC20 is ERC20 {
    address debug_owner;
    constructor() ERC20() public { debug_owner = msg.sender; }
    
    //Allows this contract to be killed by owner
    function DebugKill() public {
        require(debug_owner == address(0x0) || debug_owner == msg.sender);
        selfdestruct(msg.sender);
    }
    
    //ERC Descriptions
    function name() public pure returns (string memory) { return "Test ERC20"; }
    function symbol() public pure returns (string memory) { return "TERC20"; }
    function decimals() public pure returns (uint8) { return 18; }
    
    
    //Allow minting of tokens for everyone
    function Mint(address account, uint amount) public {
        _mint(account, amount);
    }
}