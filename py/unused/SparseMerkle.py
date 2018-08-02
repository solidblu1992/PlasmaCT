from web3 import Web3
from hexbytes import HexBytes
from util import *
    
class SparseMerkleTree:
    def __init__(self, depth=257):
        default_node = HexBytes(b'\x00'*32)
        self.default_nodes = [default_node]
        for i in range(1, depth):
            default_node = self.default_nodes[-1]
            self.default_nodes.append(Web3.sha3(HexBytes(default_node + default_node)))
        
        self.tree = [self.default_nodes[-1]]

    def add(self, uuid):
        #Format Input Data
        if (type(uuid) != bytes):
            uuid = int_to_bytes32(uuid)
            
        if (len(uuid) < 32):
            uuid = b'\x00'*(32-len(uuid)) + uuid
            
        leaf = Web3.sha3(uuid)

        searching = True
        depth = 0
        tree_section = self.tree
        bit_mask = (1 << len(self.default_nodes)-2)
        
        while (searching):
            if (len(tree_section) > 1):

            else:
                if (tree_section[0] != self.default_nodes[-depth]):
                    raise self.TreeMalformedException

                
            
        return leaf

    class TreeMalformedException(Exception):
        """tree is malformed"""
