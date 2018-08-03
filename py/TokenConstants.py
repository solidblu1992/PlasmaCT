from util import *

class Token:
    addr = 0
    H = NullPoint
    decimals = 0

    def __init__(self, addr, decimals=18):
        self.decimals = decimals
        
        if (addr == 0):
            self.H = hash_point_to_point1(G)
        else:
            self.addr = addr
            self.H = hash_addr_to_point1(addr)

TokenETH = Token(0x0000000000000000000000000000000000000000, 18)
TokenDAI = Token(0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359, 18)
TokenGNO = Token(0x6810e776880c02933d47db1b9fc05908e5386b96, 18)
TokenGNT = Token(0xa74476443119A942dE498590Fe1f2454d7D4aC0d, 18)
TokenMKR = Token(0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2, 18)
TokenOMG = Token(0xd26114cd6EE289AccF82350c8d8487fedB8A0C07, 18)
TokenRDN = Token(0x255aa6df07540cb5d3d297f0d0d4d84cb52bc8e6, 18)
TokenREP = Token(0x1985365e9f78359a9B6AD760e32412f4a445E862, 18)
TokenRPL = Token(0xb4efd85c19999d84251304bda99e90b92300bd93, 18)
