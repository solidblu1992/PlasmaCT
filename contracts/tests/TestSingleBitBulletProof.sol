pragma solidity ^0.5.0;

import "./SingleBitBulletProof.sol";

contract TestSingleBitBulletProof {
    constructor() public {}
    function DebugKill() public { selfdestruct(msg.sender); }
    function Echo() public pure returns (bool) { return true; }
    
    function GetTestProof() internal pure returns (SingleBitBulletProof.Data memory proof) {
        proof.asset_addr = 0x0000000000000000000000000000000000000000;
        proof.V = new G1Point.Data[](4);
        proof.V[0].x = 0x1b664bd98630ef642fd33826c4b0890d3f0407b6591bbfe7bbfda1a95d9a2025;
        proof.V[0].y = 0x06842488d88d2f14dc499b5faa27245aa3a4a9b62bb8837f5eb717de4f8def6c;
        proof.V[1].x = 0x10d95ae7d9a01306d856b9994d59c98e8e1a317cff725113a4e53759eebfcf03;
        proof.V[1].y = 0x175b0cf16cdb4f8173e6f843cfffa825edf47553e9eb2d600a248582be36c8ac;
        proof.V[2].x = 0x11df96fa49afbdb82d4b9ddb3fddd0ee6cafed3a19e157b5627631f835d6cbfa;
        proof.V[2].y = 0x0f985a53e45a2a1b2a3a0571b0d50cb70139740c28e08f170592ad4c78bdce0e;
        proof.V[3].x = 0x1353ed2a37224aed56c5d884c84031786337560417d6bb4418a30d520407d630;
        proof.V[3].y = 0x1c2a36ff8fa1118c10657c2d06f211f2ef9a16037c47b28a74d4ddbb5a36610f;
        proof.L = new G1Point.Data[](2);
        proof.L[0].x = 0x24267301366bd183351851d983076ba30e0ee9d2b3c684b98b81064fc1b5bd9e;
        proof.L[0].y = 0x159754b4fffd87f3ce9cf7672118b22e5ade858cebf308e02eb39132409d4360;
        proof.L[1].x = 0x231deb87cdfe223b59977a17c434d7eb066232306daa993c965c160399a2c4de;
        proof.L[1].y = 0x096a1de7a4c671aabbde7872b5c0b306e151f3855dc5c8b6c5acf90b0766fd81;
        proof.R = new G1Point.Data[](2);
        proof.R[0].x = 0x26055132da72976bfa98c86de065f1b5315df24e42c42d7e9c02020fceff32a6;
        proof.R[0].y = 0x00eb0a66765c7b1dbecab40182ad1a9303a4cb6cbae0d26ce73afe0341bde597;
        proof.R[1].x = 0x214a87c2995f94228dec4409e82f2a70405e559299fca33d0cffeb35441cbc79;
        proof.R[1].y = 0x16fa383c60575f9eb6383b75b3eaaa5eaf7ce48adff03dcb29aac4a9d4dde7bf;
        proof.A.x = 0x1670ae612910bd53b5ae4c19fd768150d6cf421775a3a3045e8c2d703c1ad243;
        proof.A.y = 0x067b51b789a90870fdd6a392c33b9c283f96785f41c3a569d7285ee52872672a;
        proof.S.x = 0x25eded14cf214f3e826408c3140f18098ea60a53d5f7c8065602a4c23bce4323;
        proof.S.y = 0x054fc9bd338714c29187bf8db8997f152fa826869e994656a01aec66b70475ae;
        proof.T1.x = 0x070d3b9facdab60cc8174db5b7e138a2467020213a867ed0b7ad3e7b176aa1b9;
        proof.T1.y = 0x0f1742a8038baba32413b9404ff0be7f163d5c911faf8d9f73d4426544c2e3c5;
        proof.T2.x = 0x03863822767eebfad8c423b02b4f75c4c75ea83b00cd1f41f8083c05855bd101;
        proof.T2.y = 0x19b994c8df3e4aacf95dc37a8c29b5c2215db25e0b56626c2b5b550f2de53798;
        proof.taux = 0x27cee75b73adfa5b0f36ddc49891ffd634f8c24796389f2ab82a2f2c3822d9df;
        proof.mu = 0x1b000aba558a4281cc0c2ac5ba1a8f460a0b9ac24cfa47249245dbd953554779;
        proof.a = 0x00e3f6a637fe237a604f2f8e3c1779fa54ebd12a0b5ea06ea741d13d19310e26;
        proof.b = 0x10962fafe70f663eb242c847d7d4cd31668a4a3c9ae0a6c209da45e68c0da622;
        proof.t = 0x0fbc586305621f81b6a3505256319754505637a7e4205279a97db3a6041d50ba;
        
        ///Resulting FiatShamirChallenges:
        //y:    0x21e121c3bfc12f8ee9e43eecd952570fd658df0d7504209d1575599aa9ee308e
        //z:    0x1edad874a34416ae848ab4701ac6193154232eece7f7efe4c3f65fa40c8d734f
        //x:    0x2726df4ed34800b2c29a6f8f357f340e41f5b64e09ce01243ad27dd307e9c869
        //x_ip: 0x259e957cd5a77d0ac409e43fb87e16d185f77c52c80d4f6f87198c111d056fbc
        //w[0]: 0x197032fb24fd64eb6ce16e3ad99d44fcd3c26aa0a169fc2a1520c6c22b59f443
        //w[1]: 0x10d4c9146be9b034f6139277e676323d5714226c367724bcd91b7576256be116
	}
	
	function Test1() public pure returns (uint8) {
	    return SingleBitBulletProof.PreCheck(GetTestProof());
	}
	
	function Test2() public pure returns (uint y, uint z, uint x, uint x_ip, uint yi, uint[] memory w, uint[] memory wi) {
	    SingleBitBulletProof.FiatShamirChallenges memory c = SingleBitBulletProof.GetFiatShamirChallenges(GetTestProof());
	    y = c.y;
	    z = c.z;
	    x = c.x;
	    x_ip = c.x_ip;
	    yi = c.yi;
	    
	    w = new uint[](c.w.length);
	    wi = new uint[](c.wi.length);
	    for (uint i = 0; i < c.w.length; i++) {
	        w[i] = c.w[i];
	        wi[i] = c.wi[i];
	    }
	}
}