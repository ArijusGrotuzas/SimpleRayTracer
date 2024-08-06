import math
import random

import numpy as np

from .objects import *


def render(
        geometry_objects,
        light,
        camera,
        background_image=None,
        shadow_samples=10
):
    """
    Renders a scene visible to the camera

    :param geometry_objects: array<Shape>
    :param light: Light
    :param camera: Camera
    :param background_image: numpy.ndarray
    :param shadow_samples: int
    :return: numpy.ndarray
    """
    # If no background image given we create a black background
    if background_image is None:
        background_image = np.zeros((camera.height, camera.width, 3), np.uint16)

    shadow_texture = np.ones((camera.height, camera.width, 3), np.uint16)
    shadow_texture.fill(255)
    image = np.copy(background_image)
    image.flags.writeable = True

    samples_y, sample_size_y = np.linspace(camera.top.y, camera.bottom.y, camera.height, retstep=True)
    samples_x, sample_size_x = np.linspace(camera.left.x, camera.right.x, camera.width, retstep=True)

    # Calculate sub-step sizes for anti-aliasing
    substep_x = sample_size_x / 4
    substep_y = sample_size_x / 4

    """ For every pixel along a view plane shoot a ray and trace back the color"""
    for i, y in enumerate(samples_y):
        for j, x in enumerate(samples_x):
            # Anti-aliasing sub-pixels
            sub_pixels = [
                Matrix4X4.mul_vector3(camera.modelMat, Vector3(x + substep_x, y + substep_y, -0.5)),
                Matrix4X4.mul_vector3(camera.modelMat, Vector3(x - substep_x, y + substep_y, -0.5)),
                Matrix4X4.mul_vector3(camera.modelMat, Vector3(x + substep_x, y - substep_y, -0.5)),
                Matrix4X4.mul_vector3(camera.modelMat, Vector3(x - substep_x, y - substep_y, -0.5))
            ]

            values = []
            for pixel in sub_pixels:
                # Define primary ray
                primary_ray = Ray(camera.center, Vector3.normalize(Vector3.subtract(pixel, camera.center)))

                color = __sample_surface(primary_ray, camera.center, geometry_objects, light, shadow_samples)

                if color is None:
                    back_val = image[i, j]
                    values.append(back_val)
                else:
                    values.append(np.array([color.r * 255, color.g * 255, color.b * 255]))

            # Save the final value to the buffer image
            image[i, j] = tuple(__calculate_average_sample(np.array(values)))

    return image


def __calculate_average_sample(samples):
    """
    Average all the samples of the surface.

    :param samples: numpy.ndarray<numpy.ndarray<int>>
    :return: numpy.ndarray<int>
    """
    height, width = samples.shape
    return np.round(np.sum(samples, axis=0) / height)


def __sample_surface(
        primary_ray,
        origin,
        geometry_objects,
        light,
        shadow_samples=10
):
    """
    Return the sample from the surface that the Ray intersects.

    :param primary_ray: Ray
    :param origin: Vector3
    :param geometry_objects: array<Shape>
    :param light: Light
    :param shadow_samples: int
    :return: Color
    """
    # Check for ray object intersection and get the closest intersection point
    distance, obj = __find_closest_intersection(primary_ray, geometry_objects)

    if not obj:
        return None

    # Get the color of the object at the specific location
    intersection = Vector3.add(primary_ray.origin, Vector3.scalar_mul(distance, primary_ray.direction))
    color = obj.color(light, origin, intersection)

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
    shadow_col = __calculate_soft_shadow(
        [
            __find_closest_distance(
                Ray(shifted_point, __get_random_light_sample(light_direction, cone_angle)),
                geometry_objects
            )
            for _ in range(shadow_samples)
        ],
        light.position,
        shifted_point
    )

    # Blend the shadow value with the ray-traced value (e.g. color at objects surface in the intersection)
    return Color.multiply(color, Color(shadow_col, shadow_col, shadow_col))


def __calculate_soft_shadow(samples, light_position, origin):
    """
    Calculates the soft shadow value at a surface.

    Sends rays from the origin to the light sample and check if they intersect any objects.
    The shadow values is calculated as a ratio of intersecting rays and non-intersecting rays.

    :param samples: array<Vector3>
    :param light_position: Vector3
    :param origin: Vector3
    :return: float
    """
    light_distance = Vector3.magnitude(Vector3.subtract(light_position, origin))

    try:
        return np.sum(np.where(np.array(samples) < light_distance, 1, 2)) / len(samples) - 1
    except ZeroDivisionError:
        return 0


# Get a random sample within a cone
def __get_random_light_sample(light_direction, cone_angle):
    """
    Get a random point on the light source, it is assumed that the light source has some radius.

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
def __find_closest_intersection(ray, geometry_objects):
    """
    Finds the first object that the ray intersects,
    and returns the distance to it from the origin of the ray along with the object itself.

    :param ray: Ray
    :param geometry_objects: array<Shape>
    :return: float, Shape
    """
    distances = np.array([obj.calculate_intersection(ray) for obj in geometry_objects])
    min_idx = np.argmin(distances)

    if math.isinf(distances[min_idx]):
        return math.inf, None

    return distances[min_idx], geometry_objects[min_idx]


def __find_closest_distance(ray, geometry_objects):
    dist, _ = __find_closest_intersection(ray, geometry_objects)

    return dist
