from bulletproofutil import *
from TokenConstants import *
BP_DEBUG_PRINTING = False

class BulletProof:    
    def __init__(self, total_commit, power10, offset, value, bf, asset_addr, V, A, S, T1, T2, taux, mu, L, R, a, b, t, N):
        #Commitment data
        self.total_commit = total_commit
        self.power10 = power10
        self.offset = offset
        self.value = value
        self.bf = bf
        self.asset_addr = asset_addr

        #Bulletproof properties
        self.V = V
        self.A = A
        self.S = S
        self.T1 = T1
        self.T2 = T2
        self.taux = taux
        self.mu = mu
        self.L = L
        self.R = R
        self.a = a
        self.b = b
        self.t = t
        self.N = N
    
    def Generate(v=0, power10=None, offset=None, gamma=None, N=32, asset_addr=0):            
        if (type(v) != list):
            v = [v]

        if (power10 == None):
            power10 = [0]*len(v)

        if (offset == None):
            offset = [0]*len(v)

        if (gamma == None):
            gamma = getRandom(len(v))
            
        if (type(power10) != list):
            power10 = [power10]

        if (type(offset) != list):
            offset = [offset]
            
        if(type(gamma) != list):
            gamma = [gamma]

        assert(len(v) == len(gamma))
        assert(len(v) == len(power10))
        assert(len(v) == len(offset))

        #Make sure M is a power of 2
        import math
        M = len(v)
        logM = math.ceil(math.log(len(v), 2))

        #Check for extra values of M, add random values
        diffM = (2**logM) - M
        if diffM > 0:
            print("warning... M(" + str(M) + ") is not a power of 2")
            print("generating " + str(diffM) + " extra values")
            M = M + diffM

        for i in range(0, diffM):
            v = v + [getRandom() % (2**N)]
            gamma = gamma + [getRandom()]

        #Make sure N is a power of 2
        logN = math.floor(math.log(N, 2))
        N = 2**logN

        logMN = logM + logN

        #Make sure enough base points have been generated
        assert(len(Gi) >= (M*N))
        assert(len(Hi) >= (M*N))

        #Get Hasset for the commitments
        if (asset_addr == 0):
            Hasset = H
        else:
            Hasset = hash_addr_to_point1(asset_addr)

        #Create V[]
        V = [NullPoint]*M
        for i in range(0, M):                
            if (v[i] == 0):
                V[i] = multiply(G, gamma[i])
            else:
                V[i] = shamir([G, Hasset], [gamma[i], v[i]])

        #Create A
        aL = [0]*(M*N)
        aR = [0]*(M*N)
        for j in range(0, M):
            for i in range(0, N):
                if (v[j] & (1 << i) != 0):
                    aL[j*N+i] = 1

                aR[j*N+i] = sSub(aL[j*N+i], 1)

        alpha = getRandom()
        A = add(pvExp(aL, aR), multiply(G, alpha))

        #Create S
        sL = getRandom(M*N)
        sR = getRandom(M*N)
        rho = getRandom()
        S = add(pvExp(sL, sR), multiply(G, rho))

        #Start hasher for Fiat-Shamir
	#Hash V[], including array length
        hasher = sha3.keccak_256()
        for j in range(0, M):
            hasher = add_point_to_hasher(hasher, V[j])

        hasher = add_point_to_hasher(hasher, A)
        hasher = add_point_to_hasher(hasher, S)
	
        y = bytes_to_int(hasher.digest()) % Ncurve
        hasher = sha3.keccak_256(int_to_bytes(y, 32))
        
        z = bytes_to_int(hasher.digest()) % Ncurve
        hasher = sha3.keccak_256(int_to_bytes(z, 32))

        #Calculate l0, l1, r0, and r1
        vp2 = vPow(2, N)
        vpy = vPow(y, M*N)
        vpyi = vPow(sInv(y), M*N)
        
        l0 = vSub(aL, [z]*(M*N))
        l1 = sL

        zerosTwos = [0]*(M*N)
        for i in range(0, M*N):
            for j in range(1, M+1):
                temp = 0
                if (i >= ((j-1)*N)) and (i < (j*N)):
                    temp = vp2[i-(j-1)*N]
                zerosTwos[i] = sAdd(zerosTwos[i], sMul(sPow(z, j+1), temp))

        r0 = vAdd(aR, [z]*(M*N))
        r0 = vMul(r0, vpy)
        r0 = vAdd(r0, zerosTwos)
        r1 = vMul(vpy, sR)

        #Calculate t0, t1, and t2 => create T1, T2
        t0 = vDot(l0, r0)
        t1 = sAdd(vDot(l0, r1), vDot(l1, r0))
        t2 = vDot(l1, r1)

        tau1 = getRandom()
        tau2 = getRandom()
        T1 = shamir([G, Hasset], [tau1, t1])
        T2 = shamir([G, Hasset], [tau2, t2])

        #Continue Fiat-Shamir
        hasher = add_point_to_hasher(hasher, T1)
        hasher = add_point_to_hasher(hasher, T2)
        x = bytes_to_int(hasher.digest()) % Ncurve
        hasher = sha3.keccak_256(int_to_bytes(x, 32))
      
        #Calculate taux and mu
        taux = sAdd(sMul(tau1, x), sMul(tau2, sSq(x)))
        for j in range(1, M+1):
            taux = sAdd(taux, sMul(sPow(z, j+1), gamma[j-1]))
        mu = sAdd(sMul(x, rho), alpha)

        #Calculate l, r, and t
        l = vAdd(l0, vScale(l1, x))
        r = vAdd(r0, vScale(r1, x))
        t = vDot(l, r)

        #Continue Fiat-Shamir
        hasher.update(int_to_bytes(taux, 32))
        hasher.update(int_to_bytes(mu, 32))
        hasher.update(int_to_bytes(t, 32))
        x_ip = bytes_to_int(hasher.digest()) % Ncurve
        hasher = sha3.keccak_256(int_to_bytes(x_ip, 32))

        #Prepare Gprime, Hprime, aprime, and bprime
        Gprime = Gi[:(M*N)]
        Hprime = pvMul(Hi[:(M*N)], vpyi)
        aprime = l
        bprime = r

        #Calculate L and R
        L = [NullPoint]*logMN
        R = [NullPoint]*logMN
        w = [0]*logMN
        
        nprime = M*N
        rounds = 0
        while (nprime > 1):
            #Halve the vector sizes
            nprime = nprime // 2

            ap1 = vSlice(aprime, 0, nprime)
            ap2 = vSlice(aprime, nprime, len(aprime))
            bp1 = vSlice(bprime, 0, nprime)
            bp2 = vSlice(bprime, nprime, len(bprime))
            gp1 = vSlice(Gprime, 0, nprime)
            gp2 = vSlice(Gprime, nprime, len(Gprime))
            hp1 = vSlice(Hprime, 0, nprime)
            hp2 = vSlice(Hprime, nprime, len(Hprime))
			
            #Calculate L and R
            cL = vDot(ap1, bp2)
            cR = vDot(bp1, ap2)

            L[rounds] = add(pvExpCustom(gp2, hp1, ap1, bp2), multiply(H, sMul(cL, x_ip)))
            R[rounds] = add(pvExpCustom(gp1, hp2, ap2, bp1), multiply(H, sMul(cR, x_ip)))

            #Update hasher for Fiat-Shamir
            hasher = add_point_to_hasher(hasher, L[rounds])
            hasher = add_point_to_hasher(hasher, R[rounds])
            w[rounds] = bytes_to_int(hasher.digest()) % Ncurve
            hasher = sha3.keccak_256(int_to_bytes(w[rounds], 32))

            #Update Gprime, Hprime, aprime, and bprime
            Gprime = pvAdd(pvScale(gp1, sInv(w[rounds])), pvScale(gp2, w[rounds]))
            Hprime = pvAdd(pvScale(hp1, w[rounds]), pvScale(hp2, sInv(w[rounds])))

            aprime = vAdd(vScale(ap1, w[rounds]), vScale(ap2, sInv(w[rounds])))
            bprime = vAdd(vScale(bp1, sInv(w[rounds])), vScale(bp2, w[rounds]))

            rounds = rounds + 1

        #Debug Printing
        if (BP_DEBUG_PRINTING):
            print()
            print("Bullet Proof Fiat-Shamir Challenges:")
            print("y:    " + hex(y))
            print("z:    " + hex(z))
            print("x:    " + hex(x))
            print("x_ip: " + hex(x_ip))
            for i in range(0, len(w)):
                print("w[" + str(i) + "]: " + hex(w[i]))

        #Generate total commitment
        total_commit = [NullPoint]*len(V)
        for i in range(0, len(V)):
            #Store base commitment
            total_commit[i] = V[i]
            
            #Multiply commitment by known power of 10, adjust blinding factor (gamma) accordingly
            if (power10[i] > 0):
                total_commit[i] = multiply(total_commit[i], 10**power10[i])
                gamma[i] = sMul(gamma[i], 10**power10[i])

            #Add known offset
            if (offset[i] > 0):
                total_commit[i] = add(total_commit[i], offset[i])

            #Update value
            v[i] = v[i]*(10**power10[i]) + offset[i]
        
        return BulletProof(total_commit, power10, offset, v, gamma, asset_addr, V, A, S, T1, T2, taux, mu, L, R, aprime[0], bprime[0], t, N)

    #Verify batch of proofs
    def VerifyMulti(proofs):
        assert (type(proofs) == list)
        assert (type(proofs[0]) == BulletProof)

        #Find longest proof
        maxLength = 0
        for p in range(0, len(proofs)):
            if (len(proofs[p].L) > maxLength):
                maxLength = len(proofs[p].L)

        maxMN = 2**maxLength

        #Initialize variables for checks
        y0 = 0              #taux
        y1 = 0              #t-(k+z+Sum(y^i))
        Y2 = NullPoint           #z-V sum
        Y3 = NullPoint           #x*T1
        Y4 = NullPoint           #x^2*T2
        Z0 = NullPoint           #A + xS
        z1 = 0              #mu
        Z2 = NullPoint           #Li / Ri sum
        z3 = 0              #(t-ab)*x_ip
        z4 = [0]*maxMN      #g scalar sum
        z5 = [0]*maxMN      #h scalar sum

        #Verify proofs
        for p in range(0, len(proofs)):
            proof = proofs[p]
            logMN = len(proof.L)
            M = 2**(logMN) // proof.N

            #Get Hasset
            if (proof.asset_addr == 0):
                Hasset = H
            else:
                Hasset = hash_addr_to_point1(proof.asset_addr)

            #Pick weight for this proof
            weight = getRandom()

            #Reconstruct Challenges
	    #Hash V[], including array length
            hasher = sha3.keccak_256()
            for j in range(0, M):
                hasher = add_point_to_hasher(hasher, proof.V[j])

	    #Continue Hasher
            hasher = add_point_to_hasher(hasher, proof.A)
            hasher = add_point_to_hasher(hasher, proof.S)
            y = bytes_to_int(hasher.digest()) % Ncurve
            
            hasher = sha3.keccak_256(int_to_bytes(y, 32))
            z = bytes_to_int(hasher.digest()) % Ncurve
            
            hasher = sha3.keccak_256(int_to_bytes(z, 32))
            hasher = add_point_to_hasher(hasher, proof.T1)
            hasher = add_point_to_hasher(hasher, proof.T2)
            x = bytes_to_int(hasher.digest()) % Ncurve
            
            hasher = sha3.keccak_256(int_to_bytes(x, 32))
            hasher.update(int_to_bytes(proof.taux, 32))
            hasher.update(int_to_bytes(proof.mu, 32))
            hasher.update(int_to_bytes(proof.t, 32))
            x_ip = bytes_to_int(hasher.digest()) % Ncurve
            hasher = sha3.keccak_256(int_to_bytes(x_ip, 32))

            #Calculate k
            #k = -([z^3 + z^4 + ... + z^(2+M)]*sum{vp2} + (z^2)*sum{vpy})
            vp2 = vPow(2, proof.N)
            vpy = vPow(y, M*proof.N)
            vpyi = vPow(sInv(y), M*proof.N)
            
            zk = sSq(z)
            k = 0
            for j in range(0, M):
                zk = sMul(zk, z)
                k = sAdd(k, zk)

            k = sNeg(sAdd(sMul(k, vSum(vp2)), sMul(sSq(z), vSum(vpy))))

            #Compute inner product challenges
            w = [0]*logMN
            for i in range(0, logMN):
                hasher = add_point_to_hasher(hasher, proof.L[i])
                hasher = add_point_to_hasher(hasher, proof.R[i])
                w[i] = bytes_to_int(hasher.digest()) % Ncurve
                hasher = sha3.keccak_256(int_to_bytes(w[i], 32))

            #Debug Printing
            if (BP_DEBUG_PRINTING):
                print()
                print("Bullet Proof Fiat-Shamir Challenges:")
                print("y:    " + hex(y))
                print("z:    " + hex(z))
                print("x:    " + hex(x))
                print("x_ip: " + hex(x_ip))
                for i in range(0, len(w)):
                    print("w[" + str(i) + "]: " + hex(w[i]))
                print("k:    " + hex(k))

            #Compute base point scalars
            for i in range(0, M*proof.N):
                gScalar = proof.a
                hScalar = sMul(proof.b, vpyi[i])

                for J in range(0, logMN):
                    j = logMN - J - 1
                    if (i & (1 << j) == 0):
                        gScalar = sMul(gScalar, sInv(w[J]))
                        hScalar = sMul(hScalar, w[J])
                    else:
                        gScalar = sMul(gScalar, w[J])
                        hScalar = sMul(hScalar, sInv(w[J]))

                gScalar = sAdd(gScalar, z)

                #Finish off hScalar
                temp = 0
                
                #Single Bit Simplification
                #z5[i] += [(z^[2+i])*(y^-i) + z - h_scalar]*weight
                if (proof.N == 1):
                    temp = sPow(z, 2+i)
                #Single Commitment Simplification
                #z5[i] += [(z^[2+i])*(y^-i) + z - h_scalar]*weight
                elif (M == 1):
                    temp = sMul(vp2[i], sPow(z, 2))
                #Full Equation
                #z5[i] += [(z^[2+i/N])*(2^[i%N])*(y^-i) + z - h_scalar]*weight
                else:
                    temp = sMul(vp2[i%proof.N], sPow(z, 2+(i//proof.N)))

                #Step common to all [temp*(y^-i) + z - h_scalar]
                temp = sSub(sAdd(sMul(temp, vpyi[i]), z), hScalar)

                #Update z4 and z5 checks for Stage 2
                z4[i] = sSub(z4[i], sMul(gScalar, weight))
                z5[i] = sAdd(z5[i], sMul(temp, weight))

            #Apply weight to remaining checks (everything but z4 and z5)
            #Stage 1 Checks
            y0 = sAdd(y0, sMul(proof.taux, weight))
            y1 = sAdd(y1, sMul(sSub(proof.t, sAdd(k, sMul(z, vSum(vpy)))), weight))

            temp = NullPoint
            for j in range(0, M):
                temp = add(temp, multiply(proof.V[j], sPow(z, j+2)))
                
            Y2 = add(Y2, multiply(temp, weight))
            Y3 = add(Y3, multiply(proof.T1, sMul(x, weight)))
            Y4 = add(Y4, multiply(proof.T2, sMul(sSq(x), weight)))

            #Stage 2 Checks
            Z0 = add(Z0, multiply(add(proof.A, multiply(proof.S, x)), weight))
            z1 = sAdd(z1, sMul(proof.mu, weight))

            temp = NullPoint
            for i in range(0, logMN):
                temp = add(temp, shamir([proof.L[i], proof.R[i]], [sSq(w[i]), sSq(sInv(w[i]))]))
            
            Z2 = add(Z2, multiply(temp, weight))
            z3 = sAdd(z3, sMul(sMul(sSub(proof.t, sMul(proof.a, proof.b)), x_ip), weight))

        #Perform all Checks
        Check1 = shamir([G, Hasset], [y0, y1])
        Check1 = add(Check1, neg(Y2))
        Check1 = add(Check1, neg(Y3))
        if (not eq(Check1, Y4)):
            print("Stage 1 Check Failed!")
            return False

        Check2 = shamir([G, H], [sNeg(z1), z3])
        Check2 = add(Check2, Z0)
        Check2 = add(Check2, pvExp(z4, z5))

        #More Debug Printing
        if (BP_DEBUG_PRINTING):
            print("y0: " + hex(y0))
            print("y1: " + hex(y1))
            print("Y2: " + hex(CompressPoint(Y2)))
            print("Y3: " + hex(CompressPoint(Y3)))
            print("Y4: " + hex(CompressPoint(Y4)))
            print()
            print("Z0: " + hex(CompressPoint(Z0)))
            print("z1: " + hex(z1))
            print("Z2: " + hex(CompressPoint(Z2)))
            print("z3: " + hex(z3))
            for i in range(0, len(z4)):
                print("z4[" + str(i) + "]: " + hex(z4[i]))
            for i in range(0, len(z5)):
                print("z5[" + str(i) + "]: " + hex(z5[i]))            
        
        if (not eq(Check2, neg(Z2))):
            print("Stage 2 Check Failed!")
            return False
        else:
            return True
        
    #On verify self, this is the only proof
    def Verify(self):
        return BulletProof.VerifyMulti([self])

    def Print(self, detailed_commitment=True):
        print()
        print("Bulletproof")
        print("# of commitments: " + str(len(self.total_commit)))
        print()

        if (self.asset_addr == 0):
            unit18 = "ETH"
            unit1 = "wei"
        else:
            unit18 = "TOKEN"
            unit1 = "wTOKEN"
        
        for i in range(0, len(self.total_commit)):
            if (detailed_commitment):
                print("Commitment " + str(i))
                
                print("total_commit: " + bytes_to_str(int_to_bytes(CompressPoint(self.total_commit[i]), 32)))
                print("power10: " + str(self.power10[i]))
                print("offset: " + str(self.offset[i]))

                pmin = (self.offset[i]) / 10**18
                pone = (self.offset[i] + 10**self.power10[i]) / 10**18
                pmax = (self.offset[i] + (2**self.N-1)*(10**self.power10[i])) / 10**18
                print("possible range: " + str(pmin) + ", " + str(pone) + ", ..., " + str(pmax) + " " + unit18)
                if (self.value != None):
                    print("[value: " + str(self.value[i] / 10**18) + " " + unit18 + " or " + str(self.value[i]) + " " + unit1 +"]")
                    print("[bf: " + hex(self.bf[i]) + "]")
                print()
                
        print("Proof Parameters:")
        print("Asset_Addr: " + bytes_to_str(int_to_bytes(self.asset_addr, 20)))
        
        for i in range(0, len(self.V)):
            print("V[" + str(i) + "]: " + bytes_to_str(int_to_bytes(CompressPoint(self.V[i]),32)))
            
        print("A:    " + bytes_to_str(int_to_bytes(CompressPoint(self.A),32)))
        print("S:    " + bytes_to_str(int_to_bytes(CompressPoint(self.S),32)))
        print("T1:   " + bytes_to_str(int_to_bytes(CompressPoint(self.T1),32)))
        print("T2:   " + bytes_to_str(int_to_bytes(CompressPoint(self.T2),32)))
        print("taux: " + bytes_to_str(int_to_bytes(self.taux, 32)))
        print("mu:   " + bytes_to_str(int_to_bytes(self.mu, 32)))

        for i in range(0, len(self.L)):
            print("L[" + str(i) + "]: " + bytes_to_str(int_to_bytes(CompressPoint(self.L[i]),32)))

        for i in range(0, len(self.R)):
            print("R[" + str(i) + "]: " + bytes_to_str(int_to_bytes(CompressPoint(self.R[i]),32)))

        print("a:    " + hex(self.a))
        print("b:    " + hex(self.b))
        print("t:    " + hex(self.t))
        print("N:    " + str(self.N))
        print()

    def Print_MEW(self):
        print("Bullet Proof:")
        print("argsSerialized:")
        print(str(1) + ",")
        combined = self.N & 0xFFFFFFFFFFFFFFFF
        combined |= (len(self.V)*2 & 0xFFFFFFFFFFFFFFFF) << 64
        combined |= (len(self.L)*2 & 0xFFFFFFFFFFFFFFFF) << 128
        combined |= (len(self.R)*2 & 0xFFFFFFFFFFFFFFFF) << 192
        print(bytes_to_str(int_to_bytes(combined,32)) + ",")
        for i in range(0, len(self.V)):
            print(point_to_str(self.V[i]) + ",")
        print(point_to_str(self.A) + ",")
        print(point_to_str(self.S) + ",")
        print(point_to_str(self.T1) + ",")
        print(point_to_str(self.T2) + ",")
        print(bytes_to_str(int_to_bytes(self.taux, 32)) + ",")
        print(bytes_to_str(int_to_bytes(self.mu, 32)) + ",")

        for i in range(0, len(self.L)):
            print(point_to_str(self.L[i]) + ",")

        for i in range(0, len(self.R)):
            print(point_to_str(self.R[i]) + ",")

        print(bytes_to_str(int_to_bytes(self.a, 32)) + ",")
        print(bytes_to_str(int_to_bytes(self.b, 32)) + ",")
        print(bytes_to_str(int_to_bytes(self.t, 32)))

        print()
        print("power10:")
        for i in range(0, len(self.power10)):
            if (i > 0):
                print(", ", end="")
                
            print(str(self.power10[i]), end="")

        print("\n")
        print("offset:")
        for i in range(0, len(self.offset)):
            if (i > 0):
                print(", ", end="")
                
            print(str(self.offset[i]), end="")

    def PrintMultiMEW(proofs):
        if (type(proofs) == BulletProof):
            proofs = [proofs]
            
        print("Bullet Proof:")
        print("argsSerialized:")
        print(str(len(proofs)) + ",")
        for i in range(0, len(proofs)):
            if (i > 0):
                print(",")

            combined = proofs[i].N & 0xFFFFFFFFFFFFFFFF
            combined |= (len(proofs[i].V)*2 & 0xFFFFFFFFFFFFFFFF) << 64
            combined |= (len(proofs[i].L)*2 & 0xFFFFFFFFFFFFFFFF) << 128
            combined |= (len(proofs[i].R)*2 & 0xFFFFFFFFFFFFFFFF) << 192
            print(bytes_to_str(int_to_bytes(combined, 32)) + ",")
            for j in range(0, len(proofs[i].V)):
                print(point_to_str(proofs[i].V[j]) + ",")
            print(point_to_str(proofs[i].A) + ",")
            print(point_to_str(proofs[i].S) + ",")
            print(point_to_str(proofs[i].T1) + ",")
            print(point_to_str(proofs[i].T2) + ",")
            print(bytes_to_str(int_to_bytes(proofs[i].taux, 32)) + ",")
            print(bytes_to_str(int_to_bytes(proofs[i].mu, 32)) + ",")

            for j in range(0, len(proofs[i].L)):
                print(point_to_str(proofs[i].L[j]) + ",")

            for j in range(0, len(proofs[i].R)):
                print(point_to_str(proofs[i].R[j]) + ",")

            print(bytes_to_str(int_to_bytes(proofs[i].a, 32)) + ",")
            print(bytes_to_str(int_to_bytes(proofs[i].b, 32)) + ",")
            print(bytes_to_str(int_to_bytes(proofs[i].t, 32)), end="")

        print("\n")
        print("power10:")
        for i in range(0, len(proofs)):
            for j in range(0, len(proofs[i].power10)):
                if (i > 0 or j > 0):
                    print(", ", end="")
                print(str(proofs[i].power10[j]), end="")

        print("\n")
        print("offset:")
        for i in range(0, len(proofs)):
            for j in range(0, len(proofs[i].offset)):
                if (i > 0 or j > 0):
                    print(", ", end="")
                print(str(proofs[i].offset[j]), end="")

    def PrintSolidityHardCoded(self):
        print("proof.asset_addr = " + bytes_to_str(int_to_bytes(self.asset_addr, 20)) + ";")
        
        print("proof.V = new G1Point.Data[](" + str(len(self.V)) + ");")
        for i in range(0, len(self.V)):
            P = normalize(self.V[i])
            print("proof.V[" + str(i) + "].x = " + bytes_to_str(int_to_bytes(P[0].n, 32)) + ";")
            print("proof.V[" + str(i) + "].y = " + bytes_to_str(int_to_bytes(P[1].n, 32)) + ";")

        print("proof.L = new G1Point.Data[](" + str(len(self.L)) + ");")
        for i in range(0, len(self.L)):
            P = normalize(self.L[i])
            print("proof.L[" + str(i) + "].x = " + bytes_to_str(int_to_bytes(P[0].n, 32)) + ";")
            print("proof.L[" + str(i) + "].y = " + bytes_to_str(int_to_bytes(P[1].n, 32)) + ";")

        print("proof.R = new G1Point.Data[](" + str(len(self.R)) + ");")
        for i in range(0, len(self.R)):
            P = normalize(self.R[i])
            print("proof.R[" + str(i) + "].x = " + bytes_to_str(int_to_bytes(P[0].n, 32)) + ";")
            print("proof.R[" + str(i) + "].y = " + bytes_to_str(int_to_bytes(P[1].n, 32)) + ";")

        P = normalize(self.A)
        print("proof.A.x = " + bytes_to_str(int_to_bytes(P[0].n, 32)) + ";")
        print("proof.A.y = " + bytes_to_str(int_to_bytes(P[1].n, 32)) + ";")

        P = normalize(self.S)
        print("proof.S.x = " + bytes_to_str(int_to_bytes(P[0].n, 32)) + ";")
        print("proof.S.y = " + bytes_to_str(int_to_bytes(P[1].n, 32)) + ";")

        P = normalize(self.T1)
        print("proof.T1.x = " + bytes_to_str(int_to_bytes(P[0].n, 32)) + ";")
        print("proof.T1.y = " + bytes_to_str(int_to_bytes(P[1].n, 32)) + ";")

        P = normalize(self.T2)
        print("proof.T2.x = " + bytes_to_str(int_to_bytes(P[0].n, 32)) + ";")
        print("proof.T2.y = " + bytes_to_str(int_to_bytes(P[1].n, 32)) + ";")

        print("proof.taux = " + bytes_to_str(int_to_bytes(self.taux, 32)) + ";")
        print("proof.mu = " + bytes_to_str(int_to_bytes(self.mu, 32)) + ";")
        print("proof.a = " + bytes_to_str(int_to_bytes(self.a, 32)) + ";")
        print("proof.b = " + bytes_to_str(int_to_bytes(self.b, 32)) + ";")
        print("proof.t = " + bytes_to_str(int_to_bytes(self.t, 32)) + ";")
            
#Single Bullet Proofs
if (True):
    bits = 32   #bits
    m = 2       #commitments per proof
    print()
    print("Generating Single Bullet Proof with " + str(m) + " commitment(s) of " + str(bits) + " bits...")

    #Generate proof(s)
    import random
    import time
    t = time.time()

    v = [random.randint(0, 2**bits-1) for i in range(0,m)]
    bp = BulletProof.Generate(v, [0]*m, [0]*m, N=bits, asset_addr=0)
    t = time.time() - t
    bp.Print_MEW()
    
    print("\n")
    print("Generate time: " + str(t / m) + "s")

    #Verify proofs(s)
    t = time.time()
    bp.Verify()
    t = time.time() - t
    print("Verify time: " + str(t / m) + "s")

#Multiple Bullet Proofs
if (False):
    p = 1       #Number of Proofs
    m = 32      #Commitments per Proof
    bits = 1
    bp = [None]*p

    print()
    print("Generating " + str(p) + " Bullet Proof(s) each with " + str(m) + " commitment(s) of " + str(bits) + " bits...")

    #Generate Proof(s)
    import random
    import time
    t = time.time()
    for i in range(0, p):
        v = [random.randint(0, 2**bits-1) for i in range(0,m)]
        bp[i] = BulletProof.Generate(v, [0]*m, [0]*m, N=bits, asset_addr=0)
    t = time.time() - t
    BulletProof.PrintMultiMEW(bp)
    print("\n")
    print("Generation time: " + str(t) + "s (" + str(t / (p * m)) + "s per commitment)")

    #Verify proofs(s)
    t = time.time()
    BulletProof.VerifyMulti(bp)
    t = time.time() - t
    print("Verify time: " + str(t) + "s (" + str(t / (p * m)) + "s per commitment)")
    print()
