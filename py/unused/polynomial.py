import sys

# python3 compatibility
if sys.version_info.major == 2:
    int_types = (int, long)  # noqa: F821
else:
    int_types = (int,)

class Polynomial:
    def __init__(self, poly = None):
        if (poly == None):
            self.poly = dict()
        else:
            assert isinstance(poly, dict)
            self.poly = poly.copy()

    def create(key_values):
        poly = dict()
        assert isinstance(key_values, (tuple, list))

        #Only one dictionary entry
        if len(key_values) == 2:
            if (isinstance(key_values[0], str)):
                assert isinstance(key_values[1], int_types)
                poly["".join(sorted(key_values[0]))] = key_values[1]

                return Polynomial(poly)
        
        #Multiple entries
        assert isinstance(key_values[0], (tuple, list))
        for i in range(0, len(key_values)):
            assert len(key_values[i]) == 2

            key = "".join(sorted(key_values[i][0]))
            if (poly.get(key) == None):
                poly[key] = key_values[i][1]
            else:
                poly[key] += key_values[i][1]
        
        return Polynomial(poly)

    def scalar(s):
        return Polynomial.create(("#", s))

    def x():
        return Polynomial.create(("x", 1))

    def y():
        return Polynomial.create(("y", 1))

    def z():
        return Polynomial.create(("z", 1))

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
        
        #Make sure variable names are only single letters (e.g. 'x', or '#')
        for i in range(0, len(variables)):
            assert len(variables[i]) == 1

        #Copy self
        out = Polynomial(self.poly)

        #For each variable, search out's keys
        for i in range(0, len(variables)):
            assert isinstance(variables[i], str)
            assert isinstance(polynomials[i], Polynomial)

            keys = list(out.poly.keys())
            values = list(out.poly.values())
            diff_out = Polynomial()

            for j in range(0, len(keys)):
                hits = 0
                newkey = ""
                for k in range(0, len(keys[j])):
                    if (keys[j][k] == variables[i]):
                       hits += 1
                    else:
                       newkey += keys[j][k]

                if (hits > 0):
                    #Remove old entry
                    out.poly.pop(keys[j])

                    #Create new polynomial to replace substitued variables with
                    if len(newkey) == 0:
                        newkey = "#"

                    diff_out += Polynomial.create([newkey, values[j]]) * polynomials[i]**hits

            #Add diff_out back into out
            out += diff_out
                
        return out

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
                    if (keys[i] == "#"):
                        new_key = other_keys[j]
                    elif (other_keys[j] == "#"):
                        new_key = keys[i]
                    #Need to modify variable name
                    else:
                        new_key = "".join(sorted(keys[i] + other_keys[j]))
                    
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
        

def GetPtDoublePolynomial():
    x = Polynomial.x()
    y = Polynomial.y()
    z = Polynomial.z()
    W = Polynomial.create(["xx", 3])
    S = Polynomial.create(["yz", 1])
    B = x * y * S
    H = W * W - B * 8
    S_squared = S * S
    newx = H * S * 2
    newy = W * (B * 4 - H) - y * y * S_squared * 8
    newz = S_squared * S * 8

    return Polynomial.create([('u', 1), ('v', 1), ('w', 1)]) - newx - newy - newz

def GetPtAddPolynomial(B_is_Generator=True):
    #Variable Point
    x1 = Polynomial.create(["x", 1])
    y1 = Polynomial.create(["y", 1])
    z1 = Polynomial.create(["z", 1])

    #Generator Point
    if (B_is_Generator):
        x2 = Polynomial.create(["#", 1])
        y2 = Polynomial.create(["#", 2])
        z2 = Polynomial.create(["#", 1])
    #2nd Variable Point
    else:
        x2 = Polynomial.create(["a", 1])
        y2 = Polynomial.create(["b", 1])
        z2 = Polynomial.create(["c", 1])
        
    U1 = y2 * z1
    U2 = y1 * z2
    V1 = x2 * z1
    V2 = x1 * z2

    #TODO: Doubling Case
    #TODO: Infinity Case

    U = U1 - U2
    V = V1 - V2
    V_squared = V * V
    V_squared_times_V2 = V_squared * V2
    V_cubed = V * V_squared
    
    W = z1 * z2
    A = U * U * W - V_cubed - V_squared_times_V2 * 2
    newx = V * A
    newy = U * (V_squared_times_V2 - A) - V_cubed * U2
    newz = V_cubed * W

    return newx + newy + newz

def Test():
    Cx = GetPtDoublePolynomial()
    var = ['x', 'y', 'z', 'u', 'v', 'w']
    equalities = [Polynomial.scalar(1), Polynomial.scalar(2), Polynomial.scalar(1),
                  Polynomial.scalar(21888242871839275222246405745257275088696311157297823662689037894645226208491),
                  Polynomial.scalar(21888242871839275222246405745257275088696311157297823662689037894645226208572),
                  Polynomial.scalar(64)]

    return Cx.evaluate(var, equalities)

field_modulus = 21888242871839275222246405745257275088696311157297823662689037894645226208583
