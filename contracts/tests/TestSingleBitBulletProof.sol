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
        proof.V = new G1Point.Data[](4);
        proof.V[0].x = 0x055c1d11aaf30bf4ff028194b8284568f003fb5b2ce2876416a7b17d1d82d0e9;
        proof.V[0].y = 0x26a16415aaa756677a11215e24efd830c6419359981b447b0928e575cd45852e;
        proof.V[1].x = 0x0682834c6ca0c63fc71089b3e502ab5fba470036a203a5808bf158cf30e4e172;
        proof.V[1].y = 0x02290703fcdb9523503906590cc67ab54c1f594eab82e0c79545e71485c1a2a5;
        proof.V[2].x = 0x2d00a57d9d58b96a91ac19b321f80d9268f0bdad78185fa45071d657100b9875;
        proof.V[2].y = 0x081bc73dfe47932eca2b478aa18a735417e2e60c0cca2a49a22489071f889a32;
        proof.V[3].x = 0x0274a3aab7876b6f235dbcd4c2ab30f024598a1b74f724c9a870c0b9c39eef96;
        proof.V[3].y = 0x2a09ef7365209002de317fbc98b9dc5b655763114aa96cef37982432f065d2fd;
        proof.L = new G1Point.Data[](2);
        proof.L[0].x = 0x1abdc43f4b97ca540375182c14323899f54e5728215ed923dce44f422dfd00ce;
        proof.L[0].y = 0x259877ccdeb7e9f09e0233657e2cb7f7fa39bcc869fce6f5a3acd4163f4a6fb3;
        proof.L[1].x = 0x2ddf1c144102900e6df62907504342fba8e1a73e37f7784accfdd178c9f24e67;
        proof.L[1].y = 0x0a1f02fa9a379c65d8a7719e283bec21d38ec15586332e587a12ef27a68577c3;
        proof.R = new G1Point.Data[](2);
        proof.R[0].x = 0x29aed92b200b459cdb75b28f7c2c3720130198246d7f5bd213f3ca414fa35922;
        proof.R[0].y = 0x2bef868764ffd4a816460512c9d633ce8c3a1dc06d20ff5bddf6c60742d6a86a;
        proof.R[1].x = 0x0f6a4e34442347dfd1a8c1e82c6ba13d4420b44c47c4222b3b1135867314dfcc;
        proof.R[1].y = 0x1e444075e72dff4981408869f7267124cfca977ca1c3bc78d4ee2a3e17d42345;
        proof.A.x = 0x26d80c58b48ab3abfba8e39a974a9fc87257745cee8d2945c50a2e175659c4e8;
        proof.A.y = 0x2881cfb197656e06d8a131a41a8dd8ef137a00bdd87469a8dc73373931213fee;
        proof.S.x = 0x0a2f3974920b9d4a6ee4f88c72f86d89919273ae14ba2cbfb111a893bd894675;
        proof.S.y = 0x09eb7819757095dde2bbf6ca2a8f98ebd7951204959619ad16d484ccb8c97a56;
        proof.T1.x = 0x06d0090c4b2b067968f08e9d3f8e76d4ca64ad9713e22d54cad000530167e1c8;
        proof.T1.y = 0x1dfbe853d7e543a3b747f73dcc6dc0ed4dd053e5951f4588ce9380f9b26cdf05;
        proof.T2.x = 0x211741c966504d8c738ff0df804dec95718b71ceb86ec55f92a5eed829bf71ca;
        proof.T2.y = 0x19c4e08b3455c3f1b54c104a17c21f7bd5f6a11793b1e5cfd5fc9c6035ace5a0;
        proof.taux = 0x04c4467b214994b3ff11d18064cb8808b277809bc6ea03241b51c368858febe9;
        proof.mu = 0x0e80f920f97256c2f0a5b2ea4d8e61e4b5b6296507108f2c4f3f3cfe4a3a6888;
        proof.a = 0x27da28e4f332c2ade531110b8b258971e550ad82399f5fcea4e0c2fb4e0442b5;
        proof.b = 0x2f63aaedc2c5269f77e2c589ca04d83e67aab2a158a9d939a905a7693c136761;
        proof.t = 0x12e0ae8f3eeba52e207728642297efb52cb9d85e458fdbc24a94bdf939901202;
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
}
