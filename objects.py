from geometry import *

"""-------------------------------------------Shapes-----------------------------------------------------------------"""


class Transform:
    def __init__(self, position, rotation):
        self.position = position
        self.rotation = rotation

    def rotateZ(self, point):
        mat = Matrix3X3.angleAxis3x3(self.rotation.z, Vector3(0, 0, 1))
        rotated_point = Matrix3X3.mulVector3(mat, point)
        return rotated_point


class Shape(Transform):
    def __init__(self, position, rotation, material):
        super().__init__(position, rotation)
        self.material = material

    def phong(self, light, camera_position, intersection, normal):
        light_direction = Vector3.normalize(Vector3.subtract(light.position, intersection))

        # RGB
        illumination = Color.black()

        # ambient
        illumination = Color.add(Color.multiply(self.material.ambient, light.ambient), illumination)

        # diffuse
        illumination = Color.add(Color.scalar_multiply(Vector3.dot(light_direction, normal),
                                                       Color.multiply(self.material.diffuse, light.diffuse)), illumination)

        # specular
        view_direction = Vector3.normalize(Vector3.subtract(camera_position, intersection))
        H = Vector3.normalize(Vector3.add(light.position, view_direction))

        illumination = Color.add(Color.scalar_multiply(Vector3.dot(normal, H) ** (
                self.material.shininess / 4), Color.multiply(self.material.specular, light.specular)), illumination)

        return illumination


class Sphere(Shape):
    def __init__(self, position, rotation, radius, material):
        super().__init__(position, rotation, material)
        self.radius = radius

    def calculate_intersection(self, ray):
        # 2 * (d x O - c)
        b = 2 * Vector3.dot(ray.direction, Vector3.subtract(ray.origin, self.position))

        # || O - c ||**2 - r**2
        c = Vector3.magnitude(Vector3.subtract(ray.origin, self.position)) ** 2 - self.radius ** 2

        # D = b**2 - 4ac, a = 1, since it's a unit vector
        discriminant = b ** 2 - 4 * c

        if discriminant > 0:
            x1 = (-b + math.sqrt(discriminant)) / 2  # x1 = (-b + D**1/2) / 2a
            x2 = (-b - math.sqrt(discriminant)) / 2  # x2 = (-b + D**1/2) / 2a

            if x1 > 0 and x2 > 0:  # Check if intersects
                return min(x1, x2)

        return None

    # Returns the surface normal specified on any point of the sphere
    def normal(self, intersection):
        return Vector3.normalize(Vector3.subtract(intersection, self.position))

    # Returns a u, v coordinates given a point on a sphere
    def spherical_map(self, intersection):
        pole = Vector3(0, 1, 0)
        equator = Vector3(-1, 0, 0)

        normal = self.normal(intersection)

        phi = math.acos(Vector3.dot(pole, normal))
        v = phi / math.pi

        theta = (math.acos(Vector3.dot(equator, normal) / math.sin(phi))) / (2 * math.pi)

        if Vector3.dot(normal, Vector3.cross(pole, equator)) > 0:
            u = theta
        else:
            u = 1 - theta

        return u, v

    # Returns a texture color given an intersection point on a sphere
    def color(self, light, camera_position, intersection):
        u, v = self.spherical_map(intersection)
        tex = self.material.texture

        height, width, channels = tex.shape

        y = int(v * (height - 1))
        x = int(u * (width - 1))

        val = tex[y, x] / 256
        col = Color(val[0], val[1], val[2])

        illumination = self.phong(light, camera_position, intersection, self.normal(intersection))

        col = Color.add(illumination, col)

        return col

    def __repr__(self):
        return f'Sphere({self.position}, {self.rotation}, {self.radius})'


class Plane(Shape):
    def __init__(self, position, rotation, material):
        super().__init__(position, rotation, material)
        self.surface_normal = Vector3.normalize(self.rotateZ(Vector3(0, 1, 0)))

    def calculate_intersection(self, ray):
        denominator = Vector3.dot(Vector3.normalize(ray.direction), self.surface_normal)

        if abs(denominator) > 1E-5:
            t = Vector3.dot(Vector3.subtract(self.position, ray.origin), self.surface_normal) / denominator

            if t >= 0:
                return t

        return None

    def normal(self, intersection):
        return self.surface_normal

    def color(self, light, camera_position, intersection):
        return self.phong(light, camera_position, intersection, self.normal(intersection))

    def __repr__(self):
        return f'Plane({self.position}, {self.rotation}, {self.surface_normal})'


"""-------------------------------------------Lights-----------------------------------------------------------------"""


class Light(Transform):
    def __init__(self, position, rotation):
        super().__init__(position, rotation)


class PointLight(Light):
    def __init__(self, position, rotation, radius, ambient, diffuse, specular):
        super().__init__(position, rotation)
        self.radius = radius
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular


class DirectionalLight(Light):
    def __init__(self, position, rotation):
        super().__init__(position, rotation)


"""-------------------------------------------Camera-----------------------------------------------------------------"""


class Camera(Transform):
    def __init__(self, position, rotation, fov):
        super().__init__(position, rotation)
        self.fov = fov


"""-------------------------------------------Material---------------------------------------------------------------"""


class Material:
    def __init__(self, ambient, diffuse, specular, shininess, texture):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.texture = texture
