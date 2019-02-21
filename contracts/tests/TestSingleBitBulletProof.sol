pragma solidity ^0.5.0;

import "./SingleBitBulletProof.sol";

contract TestSingleBitBulletProof {
    constructor() public {}
    function DebugKill() public { selfdestruct(msg.sender); }
    
    function GetTestProof() internal pure returns (SingleBitBulletProof.Data memory proof) {
	    proof.asset_addr = 0x0000000000000000000000000000000000000000;
	    
	    proof.V = new G1Point.Data[](4);
	    proof.V[0].x = 0x06a38f75a1ae89d19e50e1234d89ac51e1eb06467ffaec85997dbe374a1a9440;
	    proof.V[0].y = 0x124f28002637987ef9077b2e95b9ab2184ef0c0f9d6e978664b6f8f694e98ce1;
	    
	    proof.V[1].x = 0x1ec7ffedbf281addbdd9604d3cd8587aafda4bb3d93ac2e99c423735a615964e;
	    proof.V[1].y = 0x094d1543d7ab33bdc753023e0ff15dbe860775073bd865ba0bfe29f6c00f1db2;
	    
	    proof.V[2].x = 0x1e9140685b171a40826059eb5b6c995e769305089e58a0c758c0b6301ac67a2e;
	    proof.V[2].y = 0x188eeeed155c2e26d7e5c7eb91dfdb73c2ee88387292bca64e7a6f1e8a51d7b5;
	    
	    proof.V[3].x = 0x27eb78df6d2a6662987c4327590eac3fd8329681a2cd7d3e2658b678b618b4cc;
	    proof.V[3].y = 0x1797379875511e13d91a7d86dcaa9783d5ee111c902ddfb4a6825fd5bd35932a;
	    
	    proof.L = new G1Point.Data[](2);
	    proof.L[0].x = 0x1f48a1ebec90135b27160bc093e426640cf54fde084048e0acae7fb5a776a38b;
	    proof.L[0].y = 0x2987a6de6b72af8969e064eab40989c8f7c461d15ba727a4b9e933df086893c8;
	    
	    proof.L[1].x = 0x242c29de1b4f21af3cb7831385133077fb575c4420037538e9adfa1755c77f7b;
	    proof.L[1].y = 0x0409e30afdb6e51afb36ed9068bc52e8575b4e703a2a56dbb1082f98a4b0ef97;
	    
	    proof.R = new G1Point.Data[](2);
	    proof.R[0].x = 0x17060b1dde0b0d4ec6acb90f4164a8a2d46b1c81e48d4b63c7b2b54a478933bc;
	    proof.R[0].y = 0x1478bf5f046ea7468d3990ebb5aa7f1dd07aa98bc9c909960ab2a942a986ecc7;
	    
	    proof.R[1].x = 0x2c013bbaf34a7ac630b99f0b1f161bbb886c1f971a3decdc73fb08769df2c2a5;
	    proof.R[1].y = 0x054becd34b904a3d81f1e0e4a2ddade5e78b6a735054e41e531c00b716e1571e;
	    
	    proof.A.x = 0x07f28d1a6f3697610fcecf7ec3f0e7d423b50253eee4b07886632d427f19e60b;
	    proof.A.y = 0x107a85fc905153a9d1e9a46d6cd9da29267ab6c8eb88fd8f25b7f9663db4392e;
	    
	    proof.S.x = 0x1acdd238b530b0d3f6e7c91f27b45864fbce0a287ad2c868ba0681c7184cc5ed;
	    proof.S.y = 0x22d2fa01527f95ee7a62424b3f19713672b00d3e1e0efab1d5b24f7a024b0230;
	    
	    proof.T1.x = 0x21bf514f73d5a350ab737a59ed443f8ff821f729040d9a0ca4b5514281548688;
	    proof.T1.y = 0x075b93348727ed01b67750aaee2f964c4fbb66a5a20d0279d31b0dc0aad7cfb1;
	    
	    proof.T2.x = 0x22af6a88baad6e1672d675e2b88a8fd94dc7af885660993c01005b634a62e147;
	    proof.T2.y = 0x1135c7877f0dc8caddec8d276a68d07851899c9c51ca9d189bce05f54e5a8a56;
	    
	    proof.taux = 0x0cc70b4151910f0e9f6a05d439f10d34ccd2b6c0d7da488358dfc6204ba998be;
	    proof.mu = 0x2a68d01153144e8712723cbc05f4f49b2038888ab6460b3f401de9dcbf251e57;
	    proof.a = 0x14360f02cc94b39404d166612960310bd2e5011583591fd8d80f30eb6b454059;
	    proof.b = 0x302fc0ee23c00f9a84ddadc0f61a0696a22fb07433516664e01cd478e1e1f9c4;
	    proof.t = 0x067b3afbf9b0b93dfd14f3ee9c5e5a4c1fe1abd123ae83ad36d1dd63769e822c;
	}
	
	function Test1() public pure returns (uint8) {
	    return SingleBitBulletProof.PreCheck(GetTestProof());
	}
}
