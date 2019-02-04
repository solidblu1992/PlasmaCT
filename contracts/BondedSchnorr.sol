pragma solidity ^0.5.0;

import "./DaiInterface.sol";
import "./SchnorrSignature.sol";

contract BondedSchnorr {
    using G1Point for G1Point.Data;
    using SchnorrSignature for SchnorrSignature.Data;
    
    //"Constants"
    ERC20 DAI = ERC20(0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359);
    uint bond_price = 1 ether;  //1 ether is really 1 DAI
    uint bond_duration = 40000; //40000 blocks ~ 1 week
    
    //Bond Data
    struct SchnorrBond {
        address bondee;             //Who owns the bond?
        uint finalization_block;    //When does the bond finalize?
        
        bytes32 pub_key_hash;       //Expected Public Key
    }
    
    event NewSchnorrBond(address _bondee, uint _finalization_block, bytes sig_bytes, bytes pub_key_bytes);
    
    mapping (bytes32 => SchnorrBond) bonds;
    mapping (bytes32 => bool) finalized_bonds;
    
    //Constructor
    constructor() public {}
    function DebugKill() public { selfdestruct(msg.sender); }
    
    //View only functions
    function IsBonded(bytes32 bond_hash) public view returns (bool) {
        SchnorrBond memory bond = bonds[bond_hash];
        
        if (bond.bondee == address(0) || bond.finalization_block == 0) {
            return false;
        }
        else {
            return true;
        }
    }
    
    function IsFinalized(bytes32 bond_hash) public view returns (bool) {
        return finalized_bonds[bond_hash];
    }
    
    //State modifying functions
    function Bond(bytes memory sig_bytes, bytes memory pub_key_bytes) public returns (bool) {
        //Get hash of signature
        bytes32 h_sig = keccak256(abi.encodePacked(sig_bytes));
        bytes32 h_pub_key = keccak256(abi.encodePacked(pub_key_bytes));
        
        //Bond must be new
        if (IsBonded(h_sig)) return false;
        
        //Bondee must have enough DAI
        if (DAI.allowance(msg.sender, address(this)) < bond_price) return false;
        
        //Deduct Funds
        DAI.transferFrom(msg.sender, address(this), bond_price);
        
        //Create Bond
        uint finalization_block = block.number + bond_duration;
        bonds[h_sig] = SchnorrBond(msg.sender, finalization_block, h_pub_key);
        
        //Emit Bond information (for challengers)
        emit NewSchnorrBond(msg.sender, finalization_block, sig_bytes, pub_key_bytes);
        
        return true;
    }

    function FinalizeBond(bytes32 bond_hash) public returns (bool) {
        //If bond already finalized, do nothing
        if (IsFinalized(bond_hash)) return true;
        
        //Bond must already exist
        if (!IsBonded(bond_hash)) return false;
        
        //Bond finalization block must have been reached
        if (block.number < bonds[bond_hash].finalization_block) return false;
        
        //Finalize Bond (add to finalized list and clear bond)
        address bondee = bonds[bond_hash].bondee;
        bonds[bond_hash] = SchnorrBond(address(0), 0, 0);
        finalized_bonds[bond_hash] = true;
        
        //Return bonded DAI
        DAI.transfer(bondee, bond_price);
        return true;
    }

    function ChallengeBond(bytes memory sig_bytes, bytes memory pub_key_bytes) public returns (bool) {
        //Get hash of signature
        bytes32 h_sig = keccak256(abi.encodePacked(sig_bytes));
        bytes32 h_pub_key = keccak256(abi.encodePacked(pub_key_bytes));
        
        //Must be bonded
        if (!IsBonded(h_sig)) return false;
        
        //Expected output pub key must match
        if (bonds[h_sig].pub_key_hash != h_pub_key) return false;
        
        //Check signature
        G1Point.Data memory point = G1Point.Deserialize(pub_key_bytes);
        if (SchnorrSignature.Deserialize(sig_bytes).IsValid(point)) {
            //Signature is actually valid.  Instantly finalize the bond.
            address bondee = bonds[h_sig].bondee;
            bonds[h_sig] = SchnorrBond(address(0), 0, 0);
            finalized_bonds[h_sig] = true;
            
            //Return bonded DAI
            DAI.transfer(bondee, bond_price);
        }
        else {
            //Signature is invalid. Give bond to challenger.
            bonds[h_sig] = SchnorrBond(address(0), 0, 0);
            
            //Send DAI to challenger
            DAI.transfer(msg.sender, bond_price);
        }
    }
}