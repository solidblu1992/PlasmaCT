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

#Mainnet
TokenETH = Token(0x0000000000000000000000000000000000000000, 18)
TokenDAI = Token(0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359, 18)
TokenGNO = Token(0x6810e776880C02933D47DB1b9fc05908e5386b96, 18)
TokenGNT = Token(0xa74476443119A942dE498590Fe1f2454d7D4aC0d, 18)
TokenMKR = Token(0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2, 18)
TokenOMG = Token(0xd26114cd6EE289AccF82350c8d8487fedB8A0C07, 18)
TokenRDN = Token(0x255Aa6DF07540Cb5d3d297f0D0D4D84cb52bc8e6, 18)
TokenREP = Token(0x1985365e9f78359a9B6AD760e32412f4a445E862, 18)
TokenRPL = Token(0xB4EFd85c19999D84251304bDA99E90B92300Bd93, 18)

#Testnet
TokenGoerliTERC20 = Token(0xea100Bec80418680e55D28b655da6CbEF427275f, 18)
