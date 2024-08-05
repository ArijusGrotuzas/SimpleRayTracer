from abc import abstractmethod

from .geometry import *

"""-------------------------------------------Shapes-----------------------------------------------------------------"""


class Transform:
    def __init__(self, position, rotation, scale):
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.rotation_mat = Matrix4X4.mul_mat(
            Matrix4X4.rotation_mat(rotation.z, Vector3(0, 0, 1)),
            Matrix4X4.mul_mat(
                Matrix4X4.rotation_mat(rotation.y, Vector3(0, 1, 0)),
                Matrix4X4.mul_mat(
                    Matrix4X4.rotation_mat(rotation.x, Vector3(1, 0, 0)),
                    Matrix4X4.scaling_mat(scale)
                )
            )
        )
        self.modelMat = Matrix4X4.mul_mat(
            Matrix4X4.translation_mat(position),
            self.rotation_mat
        )


class Shape(Transform):
    def __init__(self, position, rotation, material):
        super().__init__(position, rotation, Vector3(1, 1, 1))
        self.material = material

    def phong(self, light, camera_position, intersection, normal):
        # attenuation = 1 / Vector3.magnitude(Vector3.subtract(light.position, intersection))
        light_direction = Vector3.normalize(Vector3.subtract(light.position, intersection))

        # RGB
        illumination = Color.black()

        # ambient
        illumination = Color.add(Color.multiply(self.material.ambient, light.ambient), illumination)

        # diffuse
        illumination = Color.add(
            Color.scalar_multiply(
                Vector3.dot(light_direction, normal),
                Color.multiply(self.material.diffuse, light.diffuse)
            ),
            illumination
        )

        # specular
        view_direction = Vector3.normalize(Vector3.subtract(camera_position, intersection))
        h = Vector3.normalize(Vector3.add(light.position, view_direction))

        illumination = Color.add(
            Color.scalar_multiply(
                Vector3.dot(normal, h) ** (self.material.shininess / 4),
                Color.multiply(self.material.specular, light.specular)
            ),
            illumination
        )

        return illumination

    @abstractmethod
    def normal(self, intersection):
        pass


class Sphere(Shape):
    def __init__(self, position, rotation, radius, material):
        super().__init__(position, rotation, material)
        self.radius = radius
        self.pole = Vector3(0, 1, 0)
        self.equator = Vector3(-1, 0, 0)

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

        normal = self.normal(intersection)

        phi = math.acos(Vector3.dot(self.pole, normal))
        v = phi / math.pi

        theta = (math.acos(Vector3.dot(self.equator, normal) / math.sin(phi))) / (2 * math.pi)

        if Vector3.dot(normal, Vector3.cross(self.pole, self.equator)) > 0:
            u = theta
        else:
            u = 1 - theta

        return u, v

    # Returns a texture color given an intersection point on a sphere
    def color(self, light, camera_position, intersection):
        u, v = self.spherical_map(intersection)
        tex = self.material.texture
        col = Color.black()

        if tex is not None:
            height, width, channels = tex.shape

            y = int(v * (height - 1))
            x = int(u * (width - 1))

            val = tex[y, x] / 256
            col = Color(val[0], val[1], val[2])

        illumination = self.phong(light, camera_position, intersection, self.normal(intersection))

        return Color.add(illumination, col)

    def __repr__(self):
        return f'Sphere({self.position}, {self.rotation}, {self.radius})'


class Plane(Shape):
    def __init__(self, position, rotation, material):
        super().__init__(position, rotation, material)
        self.surface_normal = Vector3.normalize(Matrix4X4.mul_vector3(self.rotation_mat, Vector3(0, 1, 0)))

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
        return self.phong(light, camera_position, intersection, self.surface_normal)

    def __repr__(self):
        return f'Plane({self.position}, {self.rotation}, {self.surface_normal})'


"""-------------------------------------------Lights-----------------------------------------------------------------"""


class Light(Transform):
    def __init__(self, position, rotation):
        super().__init__(position, rotation, Vector3.zeros())


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
    def __init__(self, position, rotation, width, height, fov):
        super().__init__(position, rotation, Vector3(fov, fov, 1))
        self.center = Matrix4X4.mul_vector3(self.modelMat, Vector3.zeros())
        self.left = Vector3(-1, 0, -1)
        self.right = Vector3(1, 0, -1)
        self.top = Vector3(0, 1 / (float(width) / height), -1)
        self.bottom = Vector3(0, -1 / (float(width) / height), -1)
        self.width = width
        self.height = height


"""-------------------------------------------Material---------------------------------------------------------------"""


class Material:
    def __init__(
            self,
            ambient=Color.white(),
            diffuse=Color.white(),
            specular=Color.white(),
            shininess=Color.white(),
            texture=None
    ):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.texture = texture
