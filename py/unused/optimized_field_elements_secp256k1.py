import rlp
from rlp.sedes import CountableList, big_endian_int

field_modulus = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

# python3 compatibility
try:
    foo = long
except:
    long = int

# Extended euclidean algorithm to find modular inverses for
# integers
def prime_field_inv(a, n):
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % n, n
    while low > 1:
        r = high//low
        nm, new = hm-lm*r, high-low*r
        lm, low, hm, high = nm, new, lm, low
    return lm % n

# A class for field elements in FQ. Wrap a number in this class,
# and it becomes a field element.
class FQ():    
    def __init__(self, n):
        if isinstance(n, self.__class__):
            self.n = n.n
        else:
            self.n = n % field_modulus
        assert isinstance(self.n, (int, long))

    def __add__(self, other):
        on = other.n if isinstance(other, FQ) else other
        return FQ((self.n + on) % field_modulus)

    def __mul__(self, other):
        on = other.n if isinstance(other, FQ) else other
        return FQ((self.n * on) % field_modulus)

    def __rmul__(self, other):
        return self * other

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        on = other.n if isinstance(other, FQ) else other
        return FQ((on - self.n) % field_modulus)

    def __sub__(self, other):
        on = other.n if isinstance(other, FQ) else other
        return FQ((self.n - on) % field_modulus)

    def __div__(self, other):
        on = other.n if isinstance(other, FQ) else other
        assert isinstance(on, (int, long))
        return FQ(self.n * prime_field_inv(on, field_modulus) % field_modulus)

    def __truediv__(self, other):
        return self.__div__(other)

    def __rdiv__(self, other):
        on = other.n if isinstance(other, FQ) else other
        assert isinstance(on, (int, long)), on
        return FQ(prime_field_inv(self.n, field_modulus) * on % field_modulus)

    def __rtruediv__(self, other):
        return self.__rdiv__(other)

    def __pow__(self, other):
        if other == 0:
            return FQ(1)
        elif other == 1:
            return FQ(self.n)
        elif other % 2 == 0:
            return (self * self) ** (other // 2)
        else:
            return ((self * self) ** int(other // 2)) * self

    def __eq__(self, other):
        if isinstance(other, FQ):
            return self.n == other.n
        else:
            return self.n == other

    def __ne__(self, other):
        return not self == other

    def __neg__(self):
        return FQ(-self.n)

    def __repr__(self):
        return repr(self.n)

    @classmethod
    def one(cls):
        return cls(1)

    @classmethod
    def zero(cls):
        return cls(0)
