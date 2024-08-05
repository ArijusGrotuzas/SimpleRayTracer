import random

import numpy as np

from .objects import *


# Convert degrees to radians
def deg2rad(degree):
    return round((degree * math.pi) / 180, 6)


# Calculate a value of a shadow given number of samples. The returned value is averaged
def calculate_soft_shadow(samples, geometry_objects, light_position, origin):
    """
    Send rays to the light along its radius and see if they intersect the sphere
    based on how many intersecting rays there are we can calculate the soft shadow as a ratio.

    :param samples: array<Vector3>
    :param geometry_objects: array<Shape>
    :param light_position: Vector3
    :param origin: Vector3
    :return: float
    """
    samples_sum = 0

    for sample in samples:
        # Define a secondary ray
        secondary_ray = Ray(origin, sample)

        # Check if the secondary ray intersects anything along the direction of light
        minimum_distance, _ = find_closest_intersection(secondary_ray, geometry_objects)
        light_distance = Vector3.magnitude(Vector3.subtract(light_position, origin))
        shadowed = minimum_distance < light_distance

        if shadowed:
            samples_sum += 1
        else:
            samples_sum += 2

    try:
        return (samples_sum / len(samples)) - 1
    except ZeroDivisionError:
        return 0


# Get a random sample within a cone
def get_random_light_sample(light_direction, cone_angle):
    """

    :param light_direction: Vector3
    :param cone_angle: float
    :return: Vector3
    """
    cos_angle = math.cos(cone_angle)

    z = random.random() * (1.0 - cos_angle) + cos_angle
    phi = random.random() * 2.0 * math.pi

    x = math.sqrt(1.0 - z * z) * math.cos(phi)
    y = math.sqrt(1.0 - z * z) * math.sin(phi)
    north = Vector3(0, 0, 1)

    axis = Vector3.normalize(Vector3.cross(north, Vector3.normalize(light_direction)))
    angle = math.acos(Vector3.dot(Vector3.normalize(light_direction), north))

    mat = Matrix4X4.rotation_mat(angle, axis)

    return Matrix4X4.mul_vector3(mat, Vector3(x, y, z))


# Find the closest intersection between a ray and an object
def find_closest_intersection(ray, geometry_objects):
    distances = [obj.calculate_intersection(ray) for obj in geometry_objects]

    minimum_dist = np.inf
    closest = None

    for i, dist in enumerate(distances):
        if dist and dist < minimum_dist:
            minimum_dist = dist
            closest = geometry_objects[i]

    return minimum_dist, closest


def render(geometry_objects, light, camera, background_image=None):
    # If no background image given we create a black background
    if background_image is None:
        background_image = np.zeros((camera.height, camera.width, 3), np.uint8)

    shadow_texture = np.ones((camera.height, camera.width, 3), np.uint8)
    shadow_texture.fill(255)
    image = np.copy(background_image)
    image.flags.writeable = True

    """ For every pixel along a view plane shoot a ray and trace back the color"""
    for i, y in enumerate(np.linspace(camera.top.y, camera.bottom.y, camera.height)):
        for j, x in enumerate(np.linspace(camera.left.x, camera.right.x, camera.width)):
            pixel = Matrix4X4.mul_vector3(camera.modelMat, Vector3(x, y, -0.5))

            # Define primary ray
            primary_ray = Ray(camera.center, Vector3.normalize(Vector3.subtract(pixel, camera.center)))

            # Check for ray object intersection and get the closest intersection point
            distance, obj = find_closest_intersection(primary_ray, geometry_objects)

            if not obj:
                continue

            # Get the color of the object at the specific location
            intersection = Vector3.add(primary_ray.origin, Vector3.scalar_mul(distance, primary_ray.direction))
            color = obj.color(light, camera.center, intersection)

            # Get the direction vector from intersection point to a light source
            shifted_point = Vector3.add(intersection, Vector3.scalar_mul(1E-5, obj.normal(intersection)))
            light_direction = Vector3.normalize(Vector3.subtract(light.position, shifted_point))

            # Soft shadows
            perp_l = Vector3.cross(light_direction, Vector3(0, 1, 0))

            if perp_l.x == 0.0 and perp_l.y == 0.0 and perp_l.z == 0.0:
                perp_l.x = 1

            # Get the vector that points in the direction of a light's edge
            light_edge = Vector3.normalize(
                Vector3.subtract(
                    Vector3.add(Vector3.scalar_mul(light.radius, perp_l), light.position),
                    intersection
                )
            )

            # Get an angle of a cone from intersection point to a light source
            cone_angle = math.acos(Vector3.dot(light_direction, light_edge)) * 2.0

            # Get the averaged color of all the shadow rays
            shadow_col = calculate_soft_shadow(
                [get_random_light_sample(light_direction, cone_angle) for i in range(36)],
                geometry_objects,
                light.position,
                shifted_point
            )

            # Write to the shadow texture
            shadow_intensity = shadow_col * 255
            shadow_texture[i, j] = (shadow_intensity, shadow_intensity, shadow_intensity)

            # Blend the shadow value with the ray-traced value (e.g. color at objects surface in the intersection)
            color = Color.multiply(color, Color(shadow_col, shadow_col, shadow_col))

            # Save the final value to the buffer image
            image[i, j] = (color.r * 255, color.g * 255, color.b * 255)

    return image
