pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./G1Point.sol";
import "./Merkel.sol";

library MultiExponentiation {
    using G1Point for G1Point.Data;
    
    struct Claim {
        //Input Data
        uint[] scalars;
        G1Point.Data[] input_points;
        
        //Intermediate results
        G1Point.Data[] intermediate_points; 
        
        //Output Data
        G1Point.Data final_result;
    }
    
    struct MerkelizedClaim {
        bytes32 scalars_mr;
        bytes32 input_points_mr;
        bytes32 intermediate_points_mr;
        uint final_result_comp;
    }
    
    function MerkelizeClaim(Claim memory c) public pure returns (MerkelizedClaim memory c_mr) {
        //Input check
        //Check lengths
        uint len = c.scalars.length;
        require(len > 0);
        require(c.input_points.length == len);
        
        if (len > 1) {
            require(c.intermediate_points.length == (len-2));
        }
        
        //Check that points are on curve
        for (uint i = 0; i < c.input_points.length; i++) {
            require(c.input_points[i].IsOnCurve());
        }
        
        for (uint i = 0; i < c.intermediate_points.length; i++) {
            require(c.intermediate_points[i].IsOnCurve());
        }
        
        require(c.final_result.IsOnCurve());
        
        //Create Merkel Roots
        bytes32[] memory b = new bytes32[](c.scalars.length);
        for (uint i = 0; i < b.length; i++) {
            b[i] = keccak256(abi.encodePacked(c.scalars[i]));
        }
        c_mr.scalars_mr = Merkel.CreateRecursive(b, 0, b.length);
        
        b= new bytes32[](c.input_points.length);
        for (uint i = 0; i < b.length; i++) {
            b[i] = c.input_points[i].HashOfPoint();
        }
        c_mr.input_points_mr = Merkel.CreateRecursive(b, 0, b.length);
        
        if (len > 1) {
            b = new bytes32[](c.intermediate_points.length);
            for (uint i = 0; i < b.length; i++) {
                b[i] = c.intermediate_points[i].HashOfPoint();
            }
            c_mr.intermediate_points_mr = Merkel.CreateRecursive(b, 0, b.length);
        }
        
        //Compress Final Result
        c_mr.final_result_comp = c.final_result.CompressPoint();
    }
}
