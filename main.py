import numpy as np
import math
import matplotlib.pyplot as plt


# Magnitude of a n-dimensional vector
def magnitude(vector):
    square_sum = 0

    for i in range(len(vector)):
        square_sum = square_sum + (vector[i] ** 2)

    return math.sqrt(square_sum)


# Normalize a n-dimensional vector
def normalize(vector):
    if magnitude(vector) != 0:
        return vector / magnitude(vector)

    return np.array([0, 0, 0])


class sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    # Calculates intersection between a sphere and a ray
    def intersect(self, ray_origin, ray_direction):
        b = 2 * np.dot(ray_direction, ray_origin - self.center)  # 2 * (d x O - c)
        c = np.linalg.norm(ray_origin - self.center) ** 2 - self.radius ** 2  # || O - c ||**2 - r**2
        discriminant = b ** 2 - 4 * c  # D = b**2 - 4ac, a = 1, since it's a unit vector

        if discriminant > 0:
            x1 = (-b + np.sqrt(discriminant)) / 2  # x1 = (-b + D**1/2) / 2a
            x2 = (-b - np.sqrt(discriminant)) / 2  # x2 = (-b + D**1/2) / 2a

            if x1 > 0 and x2 > 0:  # Check if intersects
                return min(x1, x2)

        return None

    # Returns the surface normal specified on any point of the sphere
    def surface_normal(self, point_on_sphere):
        return normalize(point_on_sphere - self.center)

    def calculate_phong(self, camera, light, objects, intersection):

        normal = self.surface_normal(intersection)
        shifted_point = intersection + 1e-5 * normal
        light_direction = normalize(light['position'] - shifted_point)

        _, min_distance = nearest_intersected_object(objects, shifted_point, light_direction)
        light_direction_magnitude = np.linalg.norm(light['position'] - intersection)
        is_shadowed = min_distance < light_direction_magnitude

        if is_shadowed:
            col = (0, 0, 0)
            return col

        normal = self.surface_normal(intersection)

        # RGB
        illumination = np.zeros(3)

        # ambient
        illumination += self.material['ambient'] * light['ambient']

        # diffuse
        illumination += self.material['diffuse'] * light['diffuse'] * np.dot(light_direction, normal)

        # specular
        view_direction = normalize(camera - intersection)
        H = normalize(light_direction + view_direction)
        illumination += self.material['specular'] * light['specular'] * np.dot(normal, H) ** (
                    self.material['shininess'] / 4)

        return np.clip(illumination, 0, 1)


class plane:
    def __init__(self, center, normal, material):
        self.center = center
        self.normal = normalize(normal)
        self.material = material

    # Calculates intersection with an infinite plane
    def intersect(self, ray_origin, ray_direction):
        denominator = np.dot(normalize(ray_direction), self.normal)

        if abs(denominator) > 0.0001:
            t = np.dot(self.center - ray_origin, self.normal) / denominator

            if t >= 0:
                return t

        return None

    def calculate_phong(self, camera, light, objects, intersection):
        shifted_point = intersection + 1e-5 * self.normal
        light_direction = normalize(light['position'] - shifted_point)

        _, min_distance = nearest_intersected_object(objects, shifted_point, light_direction)
        light_direction_magnitude = np.linalg.norm(light['position'] - intersection)
        is_shadowed = min_distance < light_direction_magnitude

        if is_shadowed:
            col = (0, 0, 0)
            return col

        # RGB
        illumination = np.zeros(3)

        # ambient
        illumination += self.material['ambient'] * light['ambient']

        # diffuse
        illumination += self.material['diffuse'] * light['diffuse'] * np.dot(light_direction, self.normal)

        # specular
        view_direction = normalize(camera - intersection)
        H = normalize(light_direction + view_direction)
        illumination += self.material['specular'] * light['specular'] * np.dot(self.normal, H) ** (
                self.material['shininess'] / 4)

        return np.clip(illumination, 0, 1)


def nearest_intersected_object(objects, ray_origin, ray_direction):
    distances = [obj.intersect(ray_origin, ray_direction) for obj in objects]
    nearest_object = None
    min_distance = np.inf

    for index, distance in enumerate(distances):
        if distance and distance < min_distance:
            min_distance = distance
            nearest_object = objects[index]

    return nearest_object, min_distance


def main():
    width = 640
    height = 480

    camera = np.array([0, 0, 1])
    ratio = float(width) / height
    screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom

    num_objects = 3

    green_material = {'ambient': np.array([0, 0.1, 0]), 'diffuse': np.array([0, 0.6, 0]),
                      'specular': np.array([1, 1, 1]), 'shininess': 60}

    purple_material = {'ambient': np.array([0.1, 0, 0.1]), 'diffuse': np.array([0.6, 0, 0.6]),
                      'specular': np.array([1, 1, 1]), 'shininess': 100}

    objects = [sphere(np.array([2 * ((i-1)/(num_objects - 1)), 0, 0]), 0.15, green_material) for i in range(num_objects)]

    objects.append(plane(np.array([0, -0.3, -2]), np.array([0, 1, 0]), purple_material))

    light = {'position': np.array([5, 5, 5]), 'ambient': np.array([1, 1, 1]), 'diffuse': np.array([1, 1, 1]),
             'specular': np.array([1, 1, 1])}

    image = np.zeros((height, width, 3))

    for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
        for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
            pixel = np.array([x, y, 0])
            origin = camera
            direction = normalize(pixel - origin)

            # check for intersections
            nearest_object, min_distance = nearest_intersected_object(objects, origin, direction)

            if nearest_object is None:
                continue

            color = nearest_object.calculate_phong(camera, light, objects,
                                                   intersection=origin + min_distance * direction)

            image[i, j] = color

        print("progress: %d/%d" % (i + 1, height))

    plt.imsave('image.png', image)


if __name__ == '__main__':
    main()
