pragma solidity ^0.5.0;

//Library for storing relevant PlasmaCT Addresses
library Addresses {
    //Goerli Testnet
    function GoerliTestERC20() internal pure returns (address) { return 0xea100Bec80418680e55D28b655da6CbEF427275f; }
    
    //Mainnet
    function DAI() internal pure returns (address) { return 0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359; }
    function GNO() internal pure returns (address) { return 0x6810e776880C02933D47DB1b9fc05908e5386b96; }
    function GNT() internal pure returns (address) { return 0xa74476443119A942dE498590Fe1f2454d7D4aC0d; }
    function MKR() internal pure returns (address) { return 0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2; }
    function OMG() internal pure returns (address) { return 0xd26114cd6EE289AccF82350c8d8487fedB8A0C07; }
    function RDN() internal pure returns (address) { return 0x255Aa6DF07540Cb5d3d297f0D0D4D84cb52bc8e6; }
    function REP() internal pure returns (address) { return 0x1985365e9f78359a9B6AD760e32412f4a445E862; }
    function RPL() internal pure returns (address) { return 0xB4EFd85c19999D84251304bDA99E90B92300Bd93; }
}