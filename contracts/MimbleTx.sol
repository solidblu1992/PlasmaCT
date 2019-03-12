pragma solidity ^0.5.0;

import "./SchnorrSignature.sol";

library MimbleTx {
    using G1Point for G1Point.Data;
    
    struct Data {
        G1Point.Data[] inputs;
        G1Point.Data[] outputs;
        SchnorrSignature.Data[] kernels;
        uint kernel_offset;
        bytes32 quantum_resistant_hash;
    }
    
    function Verify(Data memory mimble_tx) internal view returns (uint16 error_code) {
        //Check inputs
        if (mimble_tx.inputs.length == 0) return 1;
        if (mimble_tx.outputs.length == 0) return 2;
        
        for (uint i = 0; i < mimble_tx.inputs.length; i++) {
            if (!mimble_tx.inputs[i].IsOnCurve()) return uint16(0x0080 + i);
        }
        
        for (uint i = 0; i < mimble_tx.outputs.length; i++) {
            if (!mimble_tx.outputs[i].IsOnCurve()) return uint16(0x0100 + i);
        }
        
        //Recover tx kernels and sum them to a G1Point
        G1Point.Data memory KP = SchnorrSignature.RecoverMultipleSum(mimble_tx.kernels);
        if (!KP.IsOnCurve()) return 3;
        
        //Add kernel offset to this point
        KP = KP.Add(G1Point.MultiplyG1(mimble_tx.kernel_offset));
        
        //Check to see if inputs minus the outputs equals this point
        G1Point.Data memory left = mimble_tx.inputs[0];
        for (uint i = 1; i < mimble_tx.inputs.length; i++) {
            left = left.Add(mimble_tx.inputs[i]);
        }
        
        //Negate input summation
        left = left.Negate();
        
        //Add outputs
        for (uint i = 0; i < mimble_tx.outputs.length; i++) {
            left = left.Add(mimble_tx.outputs[i]);
        }
        
        //This must equal KP
        if (left.Equals(KP)) {
            return 0;
        }
        else {
            return 4;   
        }
    }

    function Verify_QuantumSecure(Data memory mimble_tx, bytes memory quantum_resistant_preimage)
        internal view returns (uint16 error_code)
    {
        //Check vanilla verification first
        error_code = Verify(mimble_tx);
        
        //Add quantum resistant step
        if (error_code == 0) {
            bytes32 hash = keccak256(abi.encodePacked(quantum_resistant_preimage));
            if (hash == mimble_tx.quantum_resistant_hash) {
                error_code = 0;
            }
            else {
                error_code = 384;   
            }
        }
    }
}
