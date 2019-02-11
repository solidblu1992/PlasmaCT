from bulletproofutil import *
from TokenConstants import *

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
        if (type(v) != list):           v = [v]
        if (power10 == None):           power10 = [0]*len(v)
        if (offset == None):            offset = [0]*len(v)
        if (gamma == None):             gamma = getRandom(len(v))
        if (type(power10) != list):     power10 = [power10]
        if (type(offset) != list):      offset = [offset]
        if (type(gamma) != list):       gamma = [gamma]
        if (type(asset_addr) != list):  asset_addr = [asset_addr]

        assert(len(v) == len(gamma))
        assert(len(v) == len(power10))
        assert(len(v) == len(offset))
        assert(len(v) == len(asset_addr))

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
        Hasset = []
        for i in range(0, M):
            if (asset_addr[i] == 0):
                Hasset += [H]
            else:
                Hasset += [hash_addr_to_point1(asset_addr[i])]

        #Create V[]
        V = [NullPoint]*M
        for i in range(0, M):                
            if (v[i] == 0):
                V[i] = multiply(G, gamma[i])
            else:
                V[i] = shamir([G, Hasset[i]], [gamma[i], v[i]])

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
        hasher = sha3.keccak_256(int_to_bytes(M*2, 32))
        for j in range(0, M):
            hasher = add_point_to_hasher(hasher, V[j])

        hasher = sha3.keccak_256(hasher.digest())
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
        #Modified to allow for multiple Hasset generators
        t0 = [0]*M
        t1 = [0]*M
        t2 = [0]*M
        t = [0]*M

        for i in range(0, M):
            i_start = i*N
            i_end = i_start + N
            t0[i] = vDot(l0[i_start:i_end], r0[i_start:i_end])
            t1[i] = sAdd(vDot(l0[i_start:i_end], r1[i_start:i_end]), vDot(l1[i_start:i_end], r0[i_start:i_end]))
            t2[i] = vDot(l1[i_start:i_end], r1[i_start:i_end])

        tau1 = getRandom()
        tau2 = getRandom()
        
        T1 = shamir_batch([G] + Hasset, [tau1] + t1)
        T2 = shamir_batch([G] + Hasset, [tau2] + t2)
        
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

        for i in range(0, M):
            i_start = i*N
            i_end = i_start + N
            t[i] = vDot(l[i_start:i_end], r[i_start:i_end])

        #Continue Fiat-Shamir
        hasher.update(int_to_bytes(taux, 32))
        hasher.update(int_to_bytes(mu, 32))

        for i in range(0, M):
            hasher.update(int_to_bytes(t[i], 32))
            
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
        if (False):
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
        y1 = dict()         #t-(k+z+Sum(y^i))
        Y2 = NullPoint      #z-V sum
        Y3 = NullPoint      #x*T1
        Y4 = NullPoint      #x^2*T2
        Z0 = NullPoint      #A + xS
        z1 = 0              #mu
        Z2 = NullPoint      #Li / Ri sum
        z3 = 0              #(t-ab)*x_ip
        z4 = [0]*maxMN      #g scalar sum
        z5 = [0]*maxMN      #h scalar sum
        Hasset = dict()

        #Verify proofs
        for p in range(0, len(proofs)):
            proof = proofs[p]
            logMN = len(proof.L)
            M = 2**(logMN) // proof.N

            #Pick weight for this proof
            weight = getRandom()

            #Reconstruct Challenges
	    #Hash V[], including array length
            hasher = sha3.keccak_256(int_to_bytes(M*2, 32))
            for j in range(0, M):
                hasher = add_point_to_hasher(hasher, proof.V[j])

	    #Continue Hasher
            hasher = sha3.keccak_256(hasher.digest())
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
            
            for i in range(0, M):
                hasher.update(int_to_bytes(proof.t[i], 32))
                
            x_ip = bytes_to_int(hasher.digest()) % Ncurve
            hasher = sha3.keccak_256(int_to_bytes(x_ip, 32))

            #Calculate k
            vp2 = vPow(2, proof.N)
            vpy = vPow(y, M*proof.N)
            vpyi = vPow(sInv(y), M*proof.N)

            k = [sSq(z)]*M
            for i in range(0, M):
                i_start = i * proof.N
                i_end = i_start + proof.N
                
                k[i] = sMul(k[i], vSum(vpy[i_start:i_end]))
                k[i] = sAdd(k[i], sMul(sPow(z, i+3), vSum(vp2)))
                k[i] = sNeg(k[i])
            
            #k = sMul(sSq(z), vSum(vpy))
            #for j in range(1, M+1):
            #    k = sAdd(k, sMul(sPow(z, j+2), vSum(vp2)))
            #k = sNeg(k)

            #Compute inner product challenges
            w = [0]*logMN
            for i in range(0, logMN):
                hasher = add_point_to_hasher(hasher, proof.L[i])
                hasher = add_point_to_hasher(hasher, proof.R[i])
                w[i] = bytes_to_int(hasher.digest()) % Ncurve
                hasher = sha3.keccak_256(int_to_bytes(w[i], 32))

            #Debug Printing
            if (False):
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
                hScalar = sSub(hScalar, sMul(sAdd(sMul(z, vpy[i]), sMul(sPow(z, 2+(i//proof.N)), vp2[i%proof.N])), vpyi[i]))

                #Update z4 and z5 checks for Stage 2
                z4[i] = sSub(z4[i], sMul(gScalar, weight))
                z5[i] = sSub(z5[i], sMul(hScalar, weight))

            #Apply weight to remaining checks (everything but z4 and z5)
            #Stage 1 Checks
            y0 = sAdd(y0, sMul(proof.taux, weight))

            for i in range(0, M):                              
                i_start = i*proof.N
                i_end = i_start + proof.N
                temp = sMul(sSub(proof.t[i], sAdd(k[i], sMul(z, vSum(vpy[i_start:i_end])))), weight)

                y1_old = y1.get(proof.asset_addr[i])
                if (y1_old == None):
                    y1[proof.asset_addr[i]] = temp

                    if (proof.asset_addr[i] == 0):
                        Hasset[proof.asset_addr[i]] = H
                    else:
                        Hasset[proof.asset_addr[i]] = hash_addr_to_point1(proof.asset_addr[i])
                else:
                    y1[proof.asset_addr[i]] = sAdd(y1_old, temp)


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

            #Calc sum(t)
            t = 0
            for i in range(0, M):
                t = sAdd(t, proof.t[i])
            z3 = sAdd(z3, sMul(sMul(sSub(t, sMul(proof.a, proof.b)), x_ip), weight))

        #Perform all Checks
        y1_items = list(y1.values())
        Hasset_items = list(Hasset.values())

        Check1 = shamir_batch([G] + Hasset_items, [y0] + y1_items)
        Check1 = add(Check1, neg(Y2))
        Check1 = add(Check1, neg(Y3))
        if (not eq(Check1, Y4)):
            print("Stage 1 Check Failed!")
            return False

        Check2 = shamir([G, H], [sNeg(z1), z3])
        Check2 = add(Check2, Z0)
        Check2 = add(Check2, pvExp(z4, z5))

        #More Debug Printing
        if (False):
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

    def Print(self):
        print()
        print("Bulletproof")
        print("# of commitments: " + str(len(self.total_commit)))
        print()

        unit18 = []
        unit1 = []
        for i in range(0, len(self.asset_addr)):
            if (self.asset_addr[i] == 0):
                unit18 += ["ETH"]
                unit1 += ["wei"]
            else:
                unit18 += ["TOKEN"]
                unit1 += ["wTOKEN (@ " + bytes_to_str(int_to_bytes(self.asset_addr[i], 20)) + ")"]
        
        for i in range(0, len(self.total_commit)):
            print("Commitment " + str(i))
            print("total_commit: " + bytes_to_str(int_to_bytes(CompressPoint(self.total_commit[i]), 32)))
            print("power10: " + str(self.power10[i]))
            print("offset: " + str(self.offset[i]))

            pmin = (self.offset[i]) / 10**18
            pone = (self.offset[i] + 10**self.power10[i]) / 10**18
            pmax = (self.offset[i] + (2**self.N-1)*(10**self.power10[i])) / 10**18
            print("possible range: " + str(pmin) + ", " + str(pone) + ", ..., " + str(pmax) + " " + unit18[i])
            if (self.value != None):
                print("[value: " + str(self.value[i] / 10**18) + " " + unit18[i] + " or " + str(self.value[i]) + " " + unit1[i] +"]")
                print("[bf: " + hex(self.bf[i]) + "]")
            print()
        
        print("Proof Parameters:")

        for i in range(0, len(self.asset_addr)):
            print("Asset_Addr[" + str(i) + "]: " + bytes_to_str(int_to_bytes(self.asset_addr[i], 20)))
            
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

        for i in range(0, len(self.t)):
            print("t[" + str(i) + "]: " + bytes_to_str(int_to_bytes(self.t[i],32)))
            
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
        print(bytes_to_str(int_to_bytes(combined, 32)) + ",")
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

        for i in range(0, len(self.t)):
            print(bytes_to_str(int_to_bytes(self.t[i],32)) + ",")

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

            for j in range(0, len(proofs[i].t)):
                print(bytes_to_str(int_to_bytes(proofs[i].t[j], 32)), end="")
                if (j < (len(proofs[i].t)-1)):
                    print(",")

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

#Single Bullet Proofs
if (False):
    bits = 16   #bits
    m = 4       #commitments per proof
    value = getRandom(m, bits, 0)
    asset_addr = getRandom(m, 160, 0)
    
    print()
    print("Generating Single Bullet Proof with " + str(m) + " commitment(s) of " + str(bits) + " bits...")

    #Generate proof(s)
    import time
    t = time.time()
    bp = BulletProof.Generate(value, [12]*m, [0]*m, N=bits, asset_addr=asset_addr)
    t = time.time() - t
    #bp.Print_MEW()
    
    print("\n")
    print("Generate time: " + str(t) + "s (" + str(t / m) + "s per commitment)")

    #Verify proofs(s)
    t = time.time()
    bp.Verify()
    t = time.time() - t
    print("Verify time: " + str(t) + "s (" + str(t / m) + "s per commitment)")

#Multiple Bullet Proofs
if (True):
    p = 2   #Number of Proofs
    m = 2   #Commitments per Proof
    bits = 64
    bp = [None]*p
    asset_addr = getRandom(m, 160, 0)

    print()
    print("Generating " + str(p) + " Bullet Proof(s) each with " + str(m) + " commitment(s) of " + str(bits) + " bits...")

    #Generate Proof(s)
    import time
    t = time.time()
    for i in range(0, p):
        value = getRandom(m, bits, 0)
        bp[i] = BulletProof.Generate(value, [17]*m, [0]*m, N=bits, asset_addr=asset_addr)
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

if (False):
    import time
    import csv
    pow10 = 0
    offset = 0
    maxlogP = 4
    maxP = 2**maxlogP
    
    #Time Trials
    with open('bulletproof.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['bits', 'commitments', 'proofs', 'generation time', 'verify time', 'verify time per proof', 'verify time per commitment'])
        for logbits in range(2, 7):
            bits = 2**logbits

            for logm in range(0, 3):
                m = 2**logm
                
                print("Generating " + str(maxP) + " proofs, each with " + str(m) + " commitments, " + str(bits) + " bits wide")

                gen_total_time = 0
                t = time.time()
                bp = []
                for p in range(0, maxP+1):
                    value = getRandom(m, bits, 0)
                    asset_addr = getRandom(m, 160, 0)
                    
                    
                    bp += [BulletProof.Generate(value, [pow10]*m, [offset]*m, N=bits, asset_addr=asset_addr)]

                gen_total_time = time.time() - t

                print("Generation time: " + str(gen_total_time) + "s, (" + str (gen_total_time / p) + "s per proof, " + str(gen_total_time / (p * m)) + "s per commitment)")
                
                for logp in range(0, maxlogP+1):
                    p = 2**logp
                    bp_p = bp[0:p]

                    ver_total_time = 0
                    t = time.time()
                    BulletProof.VerifyMulti(bp_p)
                    ver_total_time = time.time() - t
                    print ("Verification time for " + str(p) + " proofs: " + str(ver_total_time) + "s total (" + str(ver_total_time / p) + "s per proof, " + str(ver_total_time / (p * m)) + "s per commitment")
                    csvwriter.writerow([str(bits),
                                        str(m),
                                        str(p),
                                        str(gen_total_time * p / maxP),
                                        str(ver_total_time),
                                        str(ver_total_time / p),
                                        str(ver_total_time / (p*m))])    
