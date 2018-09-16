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

    def create(variable, value):
        assert isinstance(variable, str)
        
        poly = dict()
        poly["".join(sorted(variable))] = value
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
        

def test():
    x = Polynomial.x()
    y = Polynomial.y()

    xy = x+y
    return xy
    
test()
