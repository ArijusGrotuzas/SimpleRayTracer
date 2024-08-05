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
        return a.x * b.x + a.y * b.y + a.z * b.z  # + a.w * b.w

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
    def __init__(self, x, y, z, w=1):
        super().__init__(x, y, z)
        self.w = w

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

    @staticmethod
    def dot4(a, b):
        return a.x * b.x + a.y * b.y + a.z * b.z + a.w * b.w

    def __repr__(self):
        return f'Vector3({self.x}, {self.y}, {self.z}, {self.w})'


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


class Matrix4X4:
    def __init__(self, row1=Vector3.zeros(), row2=Vector3.zeros(), row3=Vector3.zeros(), row4=Vector3(0, 0, 0, 1)):
        self.row1 = row1
        self.row2 = row2
        self.row3 = row3
        self.row4 = row4
        self.column1 = Vector3(row1.x, row2.x, row3.x, row4.x)
        self.column2 = Vector3(row1.y, row2.y, row3.y, row4.y)
        self.column3 = Vector3(row1.z, row2.z, row3.z, row4.z)
        self.column4 = Vector3(row1.w, row2.w, row3.w, row4.w)

    @staticmethod
    def mul_vector3(m, v):
        return Vector3(Vector3.dot4(v, m.row1), Vector3.dot4(v, m.row2), Vector3.dot4(v, m.row3))

    @staticmethod
    def mul_mat(a, b):
        r1 = Vector3(Vector3.dot4(a.row1, b.column1), Vector3.dot4(a.row1, b.column2), Vector3.dot4(a.row1, b.column3),
                     Vector3.dot4(a.row1, b.column4))
        r2 = Vector3(Vector3.dot4(a.row2, b.column1), Vector3.dot4(a.row2, b.column2), Vector3.dot4(a.row2, b.column3),
                     Vector3.dot4(a.row2, b.column4))
        r3 = Vector3(Vector3.dot4(a.row3, b.column1), Vector3.dot4(a.row3, b.column2), Vector3.dot4(a.row3, b.column3),
                     Vector3.dot4(a.row3, b.column4))
        return Matrix4X4(r1, r2, r3)

    @staticmethod
    def rotation_mat(angle, axis):
        s = math.sin(angle)
        c = math.cos(angle)

        t = 1 - c
        x = axis.x
        y = axis.y
        z = axis.z

        return Matrix4X4(Vector3(t * x * x + c, t * x * y - s * z, t * x * z + s * y, 0),
                         Vector3(t * x * y + s * z, t * y * y + c, t * y * z - s * x, 0),
                         Vector3(t * x * z - s * y, t * y * z + s * x, t * z * z + c, 0))

    @staticmethod
    def translation_mat(translation):
        return Matrix4X4(Vector3(1, 0, 0, translation.x), Vector3(0, 1, 0, translation.y),
                         Vector3(0, 0, 1, translation.z))

    @staticmethod
    def scaling_mat(scaling):
        return Matrix4X4(Vector3(scaling.x, 0, 0, 0), Vector3(0, scaling.y, 0, 0), Vector3(0, 0, scaling.z, 0))

    @staticmethod
    def identity_mat():
        return Matrix4X4(Vector3(1, 0, 0, 0), Vector3(0, 1, 0, 0), Vector3(0, 0, 1, 0))

    def __repr__(self):
        return f'Matrix:[\n{self.row1}, \n{self.row2}, \n{self.row3}, \n{self.row4}]'
