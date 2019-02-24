pragma solidity ^0.5.0;

import "./SingleBitBulletProof.sol";

contract TestSingleBitBulletProof {
    constructor() public {}
    function DebugKill() public { selfdestruct(msg.sender); }
    function Echo() public pure returns (bool) { return true; }
    
    function TestInverse(uint[] memory values) public pure returns (uint[] memory inverses) {
        return Vector.Inverse(values);
    }
    
    function GetTestProof() internal pure returns (SingleBitBulletProof.Data memory proof) {
        proof.asset_addr = 0x0000000000000000000000000000000000000000;
        proof.V = new G1Point.Data[](8);
        proof.V[0].x = 0x0f31d9623b48f5128fd802ed695e434c4542439f54724e9664d0bf5a8e11a010;
        proof.V[0].y = 0x1419ab7d94d4f23d6bba0e31904c10d7b4503144068a20503b76cc8289946231;
        proof.V[1].x = 0x14ce41aa4c7e21aaf0e73da60d6381e1439c030daa6fea414560c6bc4e7a4465;
        proof.V[1].y = 0x204725365db964cefe19d0b6ac53d9a51911d7a37f17ac1e9d48bc922f86edc6;
        proof.V[2].x = 0x14df751dbf75678f97532459bb50d0877a70b1c2cc4046425f3392073abe4ce9;
        proof.V[2].y = 0x2b0ef3f6872b036bb7c69d56dcf583ff5ad4140ddb5a575342d7adb01fb8324f;
        proof.V[3].x = 0x0c6b62117815cb518382c49d44f00d7114020dbcc39ae25cdb82650c78bb4296;
        proof.V[3].y = 0x0945e16ec237c6b5217c7b4a81bb242e3616c7bdccc9368dbc84fe3273498995;
        proof.V[4].x = 0x2007fae2bf0497b8836e3244310a77e13c43f5d023fee2c6eb92a9d0c4fb5b4c;
        proof.V[4].y = 0x104b0a4dda54d3ec367065511fa7970ad3770b76ace1f5a507fa256c4eaf2ef7;
        proof.V[5].x = 0x0d84be934044ce3b4cfec2be4193505112d8a0b7d97bb904bad5e593cb5d912c;
        proof.V[5].y = 0x1683ce0cf76eb3d31f1278b4f2b3595760044f6b1fdbb8bf0c8b1c925099cc42;
        proof.V[6].x = 0x12c598addd86d9b399c6d0c61d57e502b64766ffcc2f6b0ac4f5213b04baa710;
        proof.V[6].y = 0x268d10aff85b76a7803ac9294b97b4c700d9ffe180953e356b9cc636d9295260;
        proof.V[7].x = 0x074d3ad623333b13e1c1e0be4b4d0bccc9d30c554364388a91a3fea6185aaff6;
        proof.V[7].y = 0x0c3a7dd9845b05bb43fe00df2b36d408578f70015c0071c2c5ecba09308197b4;
        proof.L = new G1Point.Data[](3);
        proof.L[0].x = 0x190f994609148362521c36a34051242f4c37e8829e73f3561295815cf3a4db69;
        proof.L[0].y = 0x176aa1db8b0b07d7a548f55c4d6874d15d4bc4ef37fbf7678b5367dd83daa8d6;
        proof.L[1].x = 0x1c71c1ffb8b8ed50623f998885a8ab348200fe09b2628275783fa0f7649ae227;
        proof.L[1].y = 0x192518218d0cb3d5b4fc62cd6aac22557f00ffdfba9ba80435a23f0b2c6989e9;
        proof.L[2].x = 0x217d83b055a0a782cf6f100f53b0b7131a1ccd582ff0b189be2c596b7fb567e6;
        proof.L[2].y = 0x1f41a59b0958126ec9a53cba44daee4ab92d2b7a5723069a593407aad20aede0;
        proof.R = new G1Point.Data[](3);
        proof.R[0].x = 0x22a31ad8961257c7e7e9f3ac7964f82581c04b5fad1609f751e3e0b9593974e6;
        proof.R[0].y = 0x1594a1579b83204b368fdad3911944cf7d36c56298dfb741abf39b16b86a88f7;
        proof.R[1].x = 0x23b4a05b1483275b4003179849f608e8be6b8ff8e36ad2fa3d15b017713c7081;
        proof.R[1].y = 0x1ddd31d02bc09a3c9b2b069fa61556e37869100a0eb9746075be010d3f1b8db9;
        proof.R[2].x = 0x00b8a42e68495e460ddbce18e79ec710154698450e0b5bc6dfbf0728a4639235;
        proof.R[2].y = 0x05a660c2f50078f6b53689281d6ecdbaaa9c1e8e8b809799e5e0d967c040ff05;
        proof.A.x = 0x21efdc5b3f84b8768a4c334287a415037f2154f1c2b98fee0f78b2c714dd7b0a;
        proof.A.y = 0x2ee415ff40d3726ec56d832e6194a21e924daa5de4b705475fe8f8ab9fc51af2;
        proof.S.x = 0x107d339d6e6e099a2c77527f9eaf46f51aa3e9f2172b4bfb499c450a59ae217d;
        proof.S.y = 0x22bd2651eefab6138fae154d0a20e12d9d7bd010f511638cf63e763d5e163ada;
        proof.T1.x = 0x1c178f3e44d055ad1ec1373be48785b55ee4e752480daba53864329cc3f0f5d9;
        proof.T1.y = 0x2b6469e055de52e753eb7274c86be36e52a567bbaf2a4e6eb6e486a67b0017fd;
        proof.T2.x = 0x3030388b3d32cb978e64dff6d877a1eee81e64347d3070f74b4a3bab1457b8e7;
        proof.T2.y = 0x00cfad0e6757dcc90102d666de484e2b798e7561e6ed8f5a81e3f8ff5005f4b8;
        proof.taux = 0x122ef614d657b8543f113346e0adb70309a6538dd8153e613acf312d75020bf0;
        proof.mu = 0x2b920e26b5c93e4ec7998c77d02cd0e5bad6b728f0f42d11f0ed321bf5de6526;
        proof.a = 0x019e2c317c11b8a5a76e43f75a6aef482816b0a55661b269964f652a50e2b28a;
        proof.b = 0x25410ae0c7b6d848be56885df32be694caf10224a49d2dab0f8cbb4a58fe9dfa;
        proof.t = 0x26b5975f5b03071ce7d20a8c9feeac4826976349bdaac4b3b2ec6d229152e436;
	}
	
	function Test_PreCheck() public pure returns (uint8) {
	    return SingleBitBulletProof.PreCheck(GetTestProof());
	}
	
	function Test_FiatShamir() public pure returns (uint y, uint z, uint x, uint x_ip, uint yi, uint[] memory w, uint[] memory wi) {
	    SingleBitBulletProof.Data memory proof = GetTestProof();
	    SingleBitBulletProof.FiatShamirChallenges memory c = SingleBitBulletProof.GetFiatShamirChallenges(proof);
	    y = c.y;
	    z = c.z;
	    x = c.x;
	    x_ip = c.x_ip;
	    yi = c.yi;
	    
	    w = Vector.Copy(c.w);
	    wi = Vector.Copy(c.wi);
	}
	
	function Test_Vectors() public pure returns (uint[] memory two, uint[] memory y, uint[] memory yi) {
	    SingleBitBulletProof.Data memory proof = GetTestProof();
	    SingleBitBulletProof.FiatShamirChallenges memory c = SingleBitBulletProof.GetFiatShamirChallenges(proof);
	    SingleBitBulletProof.VectorPowers memory v = SingleBitBulletProof.GetVectorPowers(c.y, c.yi, 1, proof.V.length);
	    two = Vector.Copy(v.two);
	    y = Vector.Copy(v.y);
	    yi = Vector.Copy(v.yi);
	}
	
	function Test_GetAssetH() public view returns (uint x, uint y) {
	    SingleBitBulletProof.Data memory proof = GetTestProof();
	    G1Point.Data memory Hasset = SingleBitBulletProof.GetAssetH(proof.asset_addr);
	    x = Hasset.x;
	    y = Hasset.y;
	}
	
	function Test_FromX(uint x) public view returns (uint xp, uint yp) {
	    G1Point.Data memory P = G1Point.FromX(x);
	    xp = P.x;
	    yp = P.y;
	}
	
	function Test_Stage1Check() public view returns (bool) {
	    SingleBitBulletProof.Data memory proof = GetTestProof();
	    SingleBitBulletProof.FiatShamirChallenges memory c = SingleBitBulletProof.GetFiatShamirChallenges(proof);
	    SingleBitBulletProof.VectorPowers memory v = SingleBitBulletProof.GetVectorPowers(c.y, c.yi, 1, proof.V.length);
	    G1Point.Data memory Hasset = SingleBitBulletProof.GetAssetH(proof.asset_addr);
	    
	    return SingleBitBulletProof.CalculateStage1Check(proof, c, v, Hasset);
	}
	
	function Test_Stage2Check() public view returns (uint x, uint y, uint[] memory gi_scalars, uint[] memory hi_scalars) {
	    SingleBitBulletProof.Data memory proof = GetTestProof();
	    SingleBitBulletProof.FiatShamirChallenges memory c = SingleBitBulletProof.GetFiatShamirChallenges(proof);
	    SingleBitBulletProof.VectorPowers memory v = SingleBitBulletProof.GetVectorPowers(c.y, c.yi, 1, proof.V.length);
	    G1Point.Data memory Hasset = SingleBitBulletProof.GetAssetH(proof.asset_addr);
	    
	    G1Point.Data memory P_expected;
	    (P_expected, gi_scalars, hi_scalars) = SingleBitBulletProof.CalculateStage2Check(proof, c, v, Hasset);
	    x = P_expected.x;
	    y = P_expected.y;
	}
	
	function Test_Stage2_wMultiExp() public view returns (bool) {
	    SingleBitBulletProof.Data memory proof = GetTestProof();
	    SingleBitBulletProof.FiatShamirChallenges memory c = SingleBitBulletProof.GetFiatShamirChallenges(proof);
	    SingleBitBulletProof.VectorPowers memory v = SingleBitBulletProof.GetVectorPowers(c.y, c.yi, 1, proof.V.length);
	    G1Point.Data memory Hasset = SingleBitBulletProof.GetAssetH(proof.asset_addr);
	    
	    G1Point.Data memory P_expected;
	    uint[] memory gi_scalars;
	    uint[] memory hi_scalars;
	    (P_expected, gi_scalars, hi_scalars) = SingleBitBulletProof.CalculateStage2Check(proof, c, v, Hasset);
	    
	    return SingleBitBulletProof.CalculateMultiExp(P_expected, gi_scalars, hi_scalars);
	}

    //Gas Test Functions
    function GasTest_PreCheck() public returns (uint8) {
	    return Test_PreCheck();
	}
	
	function GasTest_FiatShamir() public returns (uint y, uint z, uint x, uint x_ip, uint yi, uint[] memory w, uint[] memory wi) {
	    return Test_FiatShamir();
	}
    
    function GasTest_Vectors() public returns (uint[] memory two, uint[] memory y, uint[] memory yi) {
        return Test_Vectors();
    }
    
    function GasTest_FromX(uint x) public returns (uint xp, uint yp) {
        return Test_FromX(x);
    }
    
    function GasTest_Stage1Check() public returns (bool) {
        return Test_Stage1Check();
    }
    
    function GasTest_Stage2Check() public returns (uint x, uint y, uint[] memory gi_scalars, uint[] memory hi_scalars) {
        return Test_Stage2Check();
    }
    
    function GasTest_Stage2_wMultiExp() public returns (bool) {
        return Test_Stage2_wMultiExp();
    }
}
