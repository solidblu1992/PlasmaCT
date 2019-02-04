pragma solidity ^0.5.0;

import "./SchnorrSignature.sol";

contract TestSchnorrSignature {
    using G1Point for G1Point.Data;
    using SchnorrSignature for SchnorrSignature.Data;
    
    constructor() public {}
    function DebugKill() public { selfdestruct(msg.sender); }
    
    function Recover(bytes memory sig_bytes)
        public view returns (bytes memory pub_key)
    {
        SchnorrSignature.Data memory sig = SchnorrSignature.Deserialize(sig_bytes);
        
        //Signature:
        //0x0f9c25a001e021faf5eca5df3a2625ea5495c5c2b8111830f4b6e140423946bf16785135c512a0082f7e7a872f7830b16c16d9a860c85133d7637cc36e5f21831db44895de9f22a1be3cf081fba3188f1b535ee8001d1c900340957afb185600000000000000000000000000000000000000000000000000000000000000000b74657374732061686f7921
        //Should recover to:
        //0x2abcfabf4d00f3173559488a2b799425efcfece3e097395eb291d1040e09e04112367d044463c5bd263543da907394ec3cddfaa0b0b65c7501c93ed933c28099
    
        pub_key = sig.Recover().Serialize();
    }
    
    function RecoverMultipleSum(bytes memory sig_bytes1, bytes memory sig_bytes2)
        public view returns (bytes memory pub_key)
    {
        SchnorrSignature.Data[] memory sigs = new SchnorrSignature.Data[](2);
        
        //Signatures:
        //0x0f9c25a001e021faf5eca5df3a2625ea5495c5c2b8111830f4b6e140423946bf16785135c512a0082f7e7a872f7830b16c16d9a860c85133d7637cc36e5f21831db44895de9f22a1be3cf081fba3188f1b535ee8001d1c900340957afb185600000000000000000000000000000000000000000000000000000000000000000b74657374732061686f7921
        //0x2f50622923938d72aa137e210e98820927d95d84786e9c609009d408f0b0f3181ea562b6ee15cd585aa7a36bee31696251cc966471430f4d30690661effe1e4424171445cd8ea0e0e13d3acc49be9d1713dc970556af5319aaae930e44e37afe000000000000000000000000000000000000000000000000000000000000000b68656c6c6f20776f726c64
        //Should recover to (in either order):
        //0x2e29e590087df866dc80832f043be7bc770184aa3402385c1eaad8a70e892c15275f555486fc18581feb0d54f9870711887e5f19464e98a5f0dc3868d9b6c414
    
        sigs[0] = SchnorrSignature.Deserialize(sig_bytes1);
        sigs[1] = SchnorrSignature.Deserialize(sig_bytes2);
        pub_key = SchnorrSignature.RecoverMultipleSum(sigs).Serialize();
    }
    
    function Serialize(uint x, uint y, uint s, string memory message)
        public pure returns (bytes memory sig_bytes)
    {
        return SchnorrSignature.Serialize(SchnorrSignature.Data(G1Point.Data(x, y), s, message));
    }
    
    function Deserialize(bytes memory sig_bytes)
        public pure returns (uint x, uint y, uint s, string memory message)
    {
        //Test Vectors
        //Blank message, no length - OK
        //0x2f50622923938d72aa137e210e98820927d95d84786e9c609009d408f0b0f3181ea562b6ee15cd585aa7a36bee31696251cc966471430f4d30690661effe1e4424171445cd8ea0e0e13d3acc49be9d1713dc970556af5319aaae930e44e37afe
        
        //Blank message, but length encoded - OK
        //0x2f50622923938d72aa137e210e98820927d95d84786e9c609009d408f0b0f3181ea562b6ee15cd585aa7a36bee31696251cc966471430f4d30690661effe1e4424171445cd8ea0e0e13d3acc49be9d1713dc970556af5319aaae930e44e37afe0000000000000000000000000000000000000000000000000000000000000000
        
        //Non blank message, length encoded - OK
        //0x2f50622923938d72aa137e210e98820927d95d84786e9c609009d408f0b0f3181ea562b6ee15cd585aa7a36bee31696251cc966471430f4d30690661effe1e4424171445cd8ea0e0e13d3acc49be9d1713dc970556af5319aaae930e44e37afe000000000000000000000000000000000000000000000000000000000000000b68656c6c6f20776f726c64
        
        //Non blank message, no length encoded - FAIL
        //0x2f50622923938d72aa137e210e98820927d95d84786e9c609009d408f0b0f3181ea562b6ee15cd585aa7a36bee31696251cc966471430f4d30690661effe1e4424171445cd8ea0e0e13d3acc49be9d1713dc970556af5319aaae930e44e37afe68656c6c6f20776f726c64
        
        SchnorrSignature.Data memory sig = SchnorrSignature.Deserialize(sig_bytes);
        x = sig.R.x;
        y = sig.R.y;
        s = sig.s;
        message = sig.message;
    }
    
    function Deserialize_wG1Point(bytes memory sig_w_point_bytes)
        public pure returns (uint Px, uint Py, uint Rx, uint Ry, uint s, string memory message)
    {
        //Test Vectors
        //0x0267b562f94e5cf70e32c0d88cc6ecd6bcd713dc2ea0144d27a35b86dd6eb7a0090714460fdced6343303408f6b0e951e629ecbfd3035d92deb0f96a170b228e2f50622923938d72aa137e210e98820927d95d84786e9c609009d408f0b0f3181ea562b6ee15cd585aa7a36bee31696251cc966471430f4d30690661effe1e4424171445cd8ea0e0e13d3acc49be9d1713dc970556af5319aaae930e44e37afe000000000000000000000000000000000000000000000000000000000000000b68656c6c6f20776f726c64
        
        G1Point.Data memory point;
        SchnorrSignature.Data memory sig;
        (point, sig) = SchnorrSignature.Deserialize_wG1Point(sig_w_point_bytes);
        
        Px = point.x;
        Py = point.y;
        Rx = sig.R.x;
        Ry = sig.R.y;
        s = sig.s;
        message = sig.message;
    }
}