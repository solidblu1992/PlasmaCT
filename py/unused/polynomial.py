import sys

# python3 compatibility
if sys.version_info.major == 2:
    int_types = (int, long)  # noqa: F821
else:
    int_types = (int,)

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
          61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127,
          131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
          197, 199]

class Polynomial:
    def __init__(self, poly = None):
        if (poly == None):
            self.poly = dict()
        else:
            assert isinstance(poly, dict)
            self.poly = poly.copy()

    def create(key_values, val=None):
        poly = dict()

        #Single simple key in key_values and value in val
        #Combine into key_values = [(variable, scalar)]
        if val != None:
            assert isinstance(val, int_types)
            assert not isinstance(key_values, tuple)

            if not isinstance(key_values, list):
                key_values = [(key_values, val)]

        #Single key-value pair, make into list: key_value = [(variables, scalar)]
        if isinstance(key_values, tuple):
            key_values = [key_values]
        
        #Create Polynomial
        for i in range(0, len(key_values)):
            assert isinstance(key_values[i], tuple)
            assert len(key_values[i]) >= 2
            
            variables = key_values[i][:-1]
            assert isinstance(variables, tuple)
            for j in range(0, len(variables)):
                assert isinstance(variables[j], str)

            variables = list(variables)
            variables.sort()
            variables = tuple(variables)
            
            scalar = key_values[i][-1]
            assert isinstance(scalar, int_types)

            if (poly.get(variables) == None):
                poly[variables] = scalar
            else:
                poly[variables] += scalar
        
        return Polynomial(poly)

    def scalar(s):
        return Polynomial.create("#", s)

    def x():
        return Polynomial.create("x", 1)

    def y():
        return Polynomial.create("y", 1)

    def z():
        return Polynomial.create("z", 1)

    def is_empty(self):
        return True if len(self.poly) == 0 else False

    #Remove zero values
    def clean(self):
        keys = list(self.poly.keys())
        for i in range(0, len(keys)):
            if (self.poly.get(keys[i]) == 0):
                self.poly.pop(keys[i])

        return self

    def evaluate(self, variables, polynomials):
        if (self.is_empty()):
            return Polynomial()
        
        if not isinstance(variables, (list, tuple)):
            variables = [variables]

        if not isinstance(polynomials, (list, tuple)):
            polynomials = [polynomials]

        assert len(variables) == len(polynomials)

        #Copy self
        out = Polynomial(self.poly)

        #For each variable, search out's keys
        for i in range(0, len(variables)):
            assert len(variables[i]) == 1
            variable = variables[i][0]
            assert isinstance(variable, str)
            assert isinstance(polynomials[i], Polynomial)

            keys = list(out.poly.keys())
            values = list(out.poly.values())
            diff_out = Polynomial()

            for j in range(0, len(keys)):
                hits = 0
                newkey = []
                for k in range(0, len(keys[j])):
                    if (keys[j][k] == variable):
                       hits += 1
                    else:
                       newkey += [keys[j][k]]

                newkey.sort()
                newkey = tuple(newkey)
                
                if (hits > 0):
                    #Remove old entry
                    out.poly.pop(keys[j])

                    #Create new polynomial to replace substitued variables with
                    if len(newkey) == 0:
                        newkey = ("#",)

                    diff_out += Polynomial.create(newkey + (values[j],)) * polynomials[i]**hits

            #Add diff_out back into out
            out += diff_out
                
        return out.clean()

    def __eq__(self, other):
        assert isinstance(other, Polynomial)
        self.clean()
        other.clean()
        return self.poly == other.poly

    def __add__(self, other):
        if (isinstance(other, int_types)):
            if (other == 0):
                out = self
                return out #identity

            #Copy self
            out = Polynomial(self.poly)

            if (out.poly.get("#") == None):
                out.poly["#"] = other
            else:
                out.poly["#"] = out.poly["#"] + other
                
            return out
                
        else:
            assert(isinstance(other, Polynomial))
            
            if (self.is_empty()):
                return other
            elif (other.is_empty()):
                return self

            #Copy self
            out = Polynomial(self.poly)
            
            #Other's keys
            other_keys = list(other.poly.keys())
            other_values = list(other.poly.values())
            for i in range(0, len(other_keys)):
                if (out.poly.get(other_keys[i]) == None):
                    out.poly[other_keys[i]] = other_values[i]     
                else:
                    out.poly[other_keys[i]] += other_values[i]

            return out

    def __sub__(self, other):
        if (isinstance(other, int_types)):
            if (other == 0):
                out = self
                return out #identity

            #Copy self
            out = Polynomial(self.poly)

            if (out.poly.get("#") == None):
                out.poly["#"] = -other
            else:
                out.poly["#"] = out.poly["#"] - other
            return out
                
        else:
            assert(isinstance(other, Polynomial))
            
            if (self.is_empty()):
                return other
            elif (other.is_empty()):
                return self

            #Copy self
            out = Polynomial(self.poly)

            #Other's keys
            other_keys = list(other.poly.keys())
            other_values = list(other.poly.values())
            for i in range(0, len(other_keys)):
                if (out.poly.get(other_keys[i]) == None):
                    out.poly[other_keys[i]] = -other_values[i]
                else:
                    out.poly[other_keys[i]] -= other_values[i]

            return out

    def __mul__(self, other):        
        if (isinstance(other, int_types)):
            if (other == 0):
                return Polynomial() #empty
            elif (other == 1):
                out = self
                return pow          #identity
            elif (other == -1):
                return (-self)      #negation

            #Copy self
            out = Polynomial(self.poly)

            keys = list(out.poly.keys())
            for i in range(0, len(keys)):
                out.poly[keys[i]] = out.poly[keys[i]]*other

            return out
                
        else:
            assert(isinstance(other, Polynomial))
            if (other.is_empty()):
                return self
            elif (self.is_empty()):
                return other

            #Copy self
            out = Polynomial()

            keys = list(self.poly.keys())
            values = list(self.poly.values())
            other_keys = list(other.poly.keys())
            other_values = list(other.poly.values())
            for i in range(0, len(keys)):
                for j in range(0, len(other_keys)):
                    new_val = values[i]*other_values[j]
                    
                    #One or the other is a scalar, do not modify variable name
                    if (len(keys[i]) == 1) and (keys[i][0] == "#"):
                        new_key = other_keys[j]
                    elif (len(other_keys[j]) == 1) and (other_keys[j][0] == "#"):
                        new_key = keys[i]
                    #Need to modify variable name
                    else:
                        new_key = list(keys[i] + other_keys[j])
                        new_key.sort()
                        new_key = tuple(new_key)
                    
                    if (out.poly.get(new_key) == None):
                        out.poly[new_key] = new_val
                    else:
                        out.poly[new_key] += new_val

            return out

    def __pow__(self, other):
        if (other == 0):
            return Polynomial()
        elif (other == 1):
            return Polynomial(self.poly)
        elif other % 2 == 0:
            return (self * self) ** (other // 2)
        else:
            return ((self * self) ** int(other // 2)) * self
                            
    def __neg__(self):
        #Copy self
        out = Polynomial(self.poly)

        keys = list(self.poly.keys())
        for i in range(0, len(keys)):
            out.poly[keys[i]] = -out.poly[keys[i]]

        return out
    
    def __repr__(self):
        return repr(self.poly)
        

def GetPtDoublePolynomial(Px=Polynomial.create('Px',1), Py=Polynomial.create('Py', 1), Pz=Polynomial.create('Pz',1)):
    x = Px
    y = Py
    z = Pz
    W = x * x * 3
    S = y * z
    B = x * y * S
    H = W * W - B * 8
    S_squared = S * S
    newx = H * S * 2
    newy = W * (B * 4 - H) - y * y * S_squared * 8
    newz = S_squared * S * 8

    return (newx + newy + newz).clean()

def GetPtAddPolynomial(P1x=Polynomial.create('P1x',1), P1y=Polynomial.create('P1y',1), P1z=Polynomial.create('P1z',1),
                       P2x=Polynomial.create('P2x',1), P2y=Polynomial.create('P2y',1), P2z=Polynomial.create('P2z',1)):
    #Variable Point
    x1 = P1x
    y1 = P1y
    z1 = P1z

    x2 = P2x
    y2 = P2y
    z2 = P2z
        
    U1 = y2 * z1
    U2 = y1 * z2
    V1 = x2 * z1
    V2 = x1 * z2

    #Construct Addition Case
    U = U1 - U2
    V = V1 - V2
    V_squared = V * V
    V_squared_times_V2 = V_squared * V2
    V_cubed = V * V_squared
    
    W = z1 * z2
    A = U * U * W - V_cubed - V_squared_times_V2 * 2
    x_addG = V * A
    y_addG = U * (V_squared_times_V2 - A) - V_cubed * U2
    z_addG = V_cubed * W

    addG_sum = x_addG + y_addG + z_addG

    #Construct Infinte Point Case
    x_inf = Polynomial.create(('#', 1))
    y_inf = Polynomial.create(('#', 1))
    z_inf = Polynomial.create(('#', 0))

    inf_sum = x_inf + y_inf + z_inf

    #Construct Point Double Case
    double_sum = GetPtDoublePolynomial(P1x, P1y, P1z)
    
    out = (V1 - V2)*(addG_sum - inf_sum - double_sum)
    out = out + (U1 - U2)*(inf_sum - double_sum)
    out = out + double_sum

    return (out).clean()

field_modulus = 21888242871839275222246405745257275088696311157297823662689037894645226208583

def GetIfCasePolynomial_ieq0(i_max=(2**8-1), i_poly=Polynomial.create("i_poly", 1), f_true=Polynomial.create("f_true",1), f_false=Polynomial.create("f_false",1)):
    import math
    i_bits = math.ceil(math.log2(i_max))

    #Create bitwise variables
    bit_vars = []
    for i in range(0, i_bits):
        bit_vars = bit_vars + ["i" + str(i)]

    #Add i=0 case: (1-a)(1-b)...etc * (f_true - f_false), f_false cancels out non-zero case
    C = f_true - f_false
    for i in range(0, i_bits):
        C = C * Polynomial.create([("#", 1), (bit_vars[i], -1)])

    #Add i>0 case: just f_false
    C = C + f_false

    #Add bit breakdown proofs (i = a + 2*b + 4*c + ..., where a, b, c, ... are bits; e.g. a - a^2 = 0)
    C = C - i_poly
    for i in range(0, i_bits):
        C = C + Polynomial.create([(bit_vars[i], 2**i+1), (bit_vars[i], bit_vars[i], -1)])
        #C = C + Polynomial.create([(bit_vars[i], 2**i+1), (bit_vars[i]*2, -1)])

    return C.clean()

def GetTestEvaluation(i, i_max=(2**8-1), valid=True):
    assert i <= i_max
    import math
    i_bits = math.ceil(math.log2(i_max))

    #Create bitwise variables
    bit_vars = []
    for j in range(0, i_bits):
        bit_vars = bit_vars + [("i" + str(j),)]

    var = [("i_poly",)] + bit_vars
    values = [Polynomial.scalar(i)]

    #Create valid test vector
    if valid:
        for j in range(0, i_bits):
            #values += [Polynomial.scalar(i & (1 << j))]
            if (i & (1 << j) == 0):
                values += [Polynomial.scalar(0)]
            else:
                values += [Polynomial.scalar(1)]
                
    #Create invalid test vector (build i with non-bits)
    else:
        for j in range(0, i_bits // 2):
            mask = (3 << j*2)

            val = 0

            if (i & (1 << j*2) != 0):
                val += 1

            if (i & (1 << (j*2+1)) != 0):
                val += 2

            values += [Polynomial.scalar(val), Polynomial.scalar(0)]
            
    return (var, values)

C = GetIfCasePolynomial_ieq0()

(e_vars, e_nonzero) = GetTestEvaluation(79)
(dummy, e_zero) = GetTestEvaluation(0)
(dummy, e_invalid) = GetTestEvaluation(7, valid=False)

e = C.evaluate(e_vars, e_zero)
