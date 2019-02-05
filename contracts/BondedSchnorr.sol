pragma solidity ^0.5.0;

import "./Addresses.sol";
import "./TestERC20.sol";
import "./SchnorrSignature.sol";

contract BondedSchnorr {
    using G1Point for G1Point.Data;
    using SchnorrSignature for SchnorrSignature.Data;
    
    //"Constants"
    ERC20 DAI = ERC20( Addresses.GoerliTestERC20() );
    uint bond_price = 1 ether;  //1 ether is really 1 DAI
    uint bond_duration = 40000; //40000 blocks ~ 1 week
    
    //Bond Data
    struct SchnorrBond {
        address bondee;             //Who owns the bond?
        uint finalization_block;    //When does the bond finalize?
    }
    
    event NewSchnorrBond(address _bondee, uint _finalization_block, bytes32 sig_hash, bytes sig_w_point_bytes);
    event SchnorrBondFinalized(bytes32 sig_hash);
    event SchnorrBondRejected(bytes32 sig_hash);
    
    mapping (bytes32 => SchnorrBond) bonds;
    mapping (bytes32 => bool) finalized_bonds;
    
    ///Constructor
    constructor() public {}
    function DebugKill() public { selfdestruct(msg.sender); }
    
    ///View only functions
    //Check to see if a signature is currently bonded
    function IsBonded(bytes32 bond_hash) public view returns (bool) {
        SchnorrBond memory bond = bonds[bond_hash];
        
        if (bond.bondee == address(0) || bond.finalization_block == 0) {
            return false;
        }
        else {
            return true;
        }
    }
    
    //Check to see if a signature is finalized (that is, valid)
    function IsFinalized(bytes32 bond_hash) public view returns (bool) {
        return finalized_bonds[bond_hash];
    }
    
    ///State modifying functions
    //Bond a signature. Bet DAI that it is valid, anyone can challenge
    function Bond(bytes memory sig_w_point_bytes) public returns (bool) {
        //Get hash of signature
        bytes32 h_sig = keccak256(abi.encodePacked(sig_w_point_bytes));
        
        //Bond must be new
        if (IsBonded(h_sig)) return false;
        
        //Bondee must have enough DAI
        if (DAI.allowance(msg.sender, address(this)) < bond_price) return false;
        
        //Deduct Funds
        DAI.transferFrom(msg.sender, address(this), bond_price);
        
        //Create Bond
        uint finalization_block = block.number + bond_duration;
        bonds[h_sig] = SchnorrBond(msg.sender, finalization_block);
        
        //Emit Bond information (for challengers)
        emit NewSchnorrBond(msg.sender, finalization_block, h_sig, sig_w_point_bytes);
        
        return true;
    }

    //Finalize a bond. After finalization block, mark the signature as valid and return DAI
    function FinalizeBond(bytes32 bond_hash) public returns (bool) {
        //If bond already finalized, do nothing
        if (IsFinalized(bond_hash)) return true;
        
        //Bond must already exist
        if (!IsBonded(bond_hash)) return false;
        
        //Bond finalization block must have been reached
        if (block.number < bonds[bond_hash].finalization_block) return false;
        
        //Finalize Bond (add to finalized list and clear bond)
        address bondee = bonds[bond_hash].bondee;
        bonds[bond_hash] = SchnorrBond(address(0), 0);
        finalized_bonds[bond_hash] = true;
        emit SchnorrBondFinalized(bond_hash);
        
        //Return bonded DAI
        DAI.transfer(bondee, bond_price);
        return true;
    }

    //Challenge a bond. If bonded signature is invalid, give DAI bond to challengee.
    //Can also be used to instantly finalize a bond while costing more gas.
    function ChallengeBond(bytes memory sig_w_point_bytes) public returns (bool) {
        //Get hash of signature
        bytes32 h_sig = keccak256(abi.encodePacked(sig_w_point_bytes));
        
        //Must be bonded
        if (!IsBonded(h_sig)) return false;
        
        //Check signature
        G1Point.Data memory point;
        SchnorrSignature.Data memory sig;
        (point, sig) = SchnorrSignature.Deserialize_wG1Point(sig_w_point_bytes);
        
        if (sig.IsValid(point)) {
            //Signature is actually valid.  Instantly finalize the bond.
            address bondee = bonds[h_sig].bondee;
            bonds[h_sig] = SchnorrBond(address(0), 0);
            finalized_bonds[h_sig] = true;
            emit SchnorrBondFinalized(h_sig);
            
            //Return bonded DAI
            DAI.transfer(bondee, bond_price);
        }
        else {
            //Signature is invalid. Give bond to challenger.
            bonds[h_sig] = SchnorrBond(address(0), 0);
            emit SchnorrBondRejected(h_sig);
            
            //Send DAI to challenger
            DAI.transfer(msg.sender, bond_price);
        }
    }
    
	function Debug_GetHash(bytes memory b) public pure returns (bytes32 hash) {
	    hash = keccak256(abi.encodePacked(b));
	}
}