import math

"""-------------------------------------------Vectors, Points, Tuples------------------------------------------------"""


class Tuple:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def add(a, b):
        return Vector3(a.x + b.x, a.y + b.y, a.z + b.z)

    @staticmethod
    def subtract(a, b):
        return Vector3(a.x - b.x, a.y - b.y, a.z - b.z)

    @staticmethod
    def multiply(a, b):
        return Vector3(a.x * b.x, a.y * b.y, a.z * b.z)

    @staticmethod
    def scalar_mul(a, v):
        return Vector3(v.x * a, v.y * a, v.z * a)

    @staticmethod
    def scalar_div(a, v):
        return Vector3(v.x / a, v.y / a, v.z / a)

    @staticmethod
    def dot(a, b):
        return a.x * b.x + a.y * b.y + a.z * b.z

    @staticmethod
    def cross(a, b):
        return Vector3((a.y * b.z) - (a.z * b.y), (a.z * b.x) - (a.x * b.z), (a.x * b.y) - (a.y * b.x))


class Point(Tuple):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def zeros():
        return Point(0, 0, 0)

    @staticmethod
    def units():
        return Point(1, 1, 1)

    def __repr__(self):
        return f'Vector3("{self.x}", "{self.y}", "{self.z}")'


class Vector3(Tuple):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.w = 0

    @staticmethod
    def zeros():
        return Vector3(0, 0, 0)

    @staticmethod
    def units():
        return Vector3(1, 1, 1)

    @staticmethod
    def magnitude(v):
        return math.sqrt(pow(v.x, 2) + pow(v.y, 2) + pow(v.z, 2))

    @staticmethod
    def normalize(v):
        mag = math.sqrt(pow(v.x, 2) + pow(v.y, 2) + pow(v.z, 2))

        try:
            return Vector3(v.x / mag, v.y / mag, v.z / mag)
        except ZeroDivisionError:
            print("Division by zero! Returning zero vector...")
            return Vector3(0, 0, 0)

    def __repr__(self):
        return f'Vector3({self.x}, {self.y}, {self.z})'


"""-------------------------------------------Color------------------------------------------------------------------"""


class Color:
    def __init__(self, r, g, b):
        self.r = max(0, min(1, r))
        self.g = max(0, min(1, g))
        self.b = max(0, min(1, b))

    @staticmethod
    def white():
        return Color(1, 1, 1)

    @staticmethod
    def black():
        return Color(0, 0, 0)

    @staticmethod
    def add(a, b):
        return Color(min(1, a.r + b.r), min(1, a.g + b.g), min(1, a.b + b.b))

    @staticmethod
    def multiply(a, b):
        return Color(min(1, a.r * b.r), min(1, a.g * b.g), min(1, a.b * b.b))

    @staticmethod
    def scalar_multiply(a, b):
        return Color(min(1, a * b.r), min(1, a * b.g), min(1, a * b.b))

    @staticmethod
    def subtract(a, b):
        return Color(max(0, a.r - b.r), max(0, a.g - b.g), max(0, a.b - b.b))

    def __repr__(self):
        return f'Color("{self.r}", "{self.g}", "{self.b}")'


"""-------------------------------------------Ray--------------------------------------------------------------------"""


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def __repr__(self):
        return f'Ray({self.origin}, {self.direction})'


"""-------------------------------------------Matrices---------------------------------------------------------------"""


class Matrix3X3:
    def __init__(self, row1, row2, row3):
        self.row1 = row1
        self.row2 = row2
        self.row3 = row3

    @staticmethod
    def mulVector3(m, v):
        x = Vector3.dot(v, m.row1)
        y = Vector3.dot(v, m.row2)
        z = Vector3.dot(v, m.row3)

        return Vector3(x, y, z)

    @staticmethod
    def angleAxis3x3(angle, axis):
        s = math.sin(angle)
        c = math.cos(angle)

        t = 1 - c
        x = axis.x
        y = axis.y
        z = axis.z

        return Matrix3X3(Vector3(t * x * x + c, t * x * y - s * z, t * x * z + s * y),
                         Vector3(t * x * y + s * z, t * y * y + c, t * y * z - s * x),
                         Vector3(t * x * z - s * y, t * y * z + s * x, t * z * z + c))

    def __repr__(self):
        return f'Matrix:\n{self.row1},\n{self.row2},\n{self.row3}'


class RotationMatrixZ(Matrix3X3):
    def __init__(self, theta):
        super().__init__(Vector3(math.cos(theta), -math.sin(theta), 0),
                         Vector3(math.sin(theta), math.cos(theta), 0),
                         Vector3(0, 0, 1))
