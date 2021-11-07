import os
import random

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from definitions import TEXTURES_PATH, RESULTS_PATH
from objects import *


# Calculate a value of a shadow given number of samples. The returned value is averaged
def soft_shadow(samples, objects, light, origin):
    samples_sum = 0

    for samp in samples:
        # Define a secondary ray
        secondary_ray = Ray(origin, samp)

        # Check if the secondary ray intersects anything along the direction of light
        minimum_distance, _ = closest_intersection(secondary_ray, objects)
        light_distance = Vector3.magnitude(Vector3.subtract(light.position, origin))
        shadowed = minimum_distance < light_distance

        if shadowed:
            samples_sum += 2
        else:
            samples_sum += 1

    return (samples_sum / len(samples)) - 1


# Get a random sample within a cone
def light_sample(direction, cone_angle):
    cosAngle = math.cos(cone_angle)

    z = random.random() * (1.0 - cosAngle) + cosAngle
    phi = random.random() * 2.0 * math.pi

    x = math.sqrt(1.0 - z * z) * math.cos(phi)
    y = math.sqrt(1.0 - z * z) * math.sin(phi)
    north = Vector3(0, 0, 1)

    axis = Vector3.normalize(Vector3.cross(north, Vector3.normalize(direction)))
    angle = math.acos(Vector3.dot(Vector3.normalize(direction), north))

    mat = Matrix3X3.angleAxis3x3(angle, axis)

    return Matrix3X3.mulVector3(mat, Vector3(x, y, z))


# Find the closest intersection between a ray and an object
def closest_intersection(ray, objects):
    distances = [obj.calculate_intersection(ray) for obj in objects]

    minimum_dist = np.inf
    closest = None

    for i, dist in enumerate(distances):
        if dist and dist < minimum_dist:
            minimum_dist = dist
            closest = objects[i]

    return minimum_dist, closest


def main():
    """Import the textures"""
    earth_texture = Image.open(os.path.join(TEXTURES_PATH, 'earth.jpg'))
    earth_tex = np.asarray(earth_texture)

    background = Image.open(os.path.join(TEXTURES_PATH, 'space1.jpg'))
    back = np.asarray(background)

    """Define objects present in the scene"""
    camera = Camera(Vector3(0, 0, 1), Vector3(0, 0, 0), 1)

    light = PointLight(Vector3(5, 5, 5), Vector3.zeros(), 1, Color(1, 1, 1), Color(0.945, 0.703, 0.253),
                       Color(0.945, 0.703, 0.253))

    mat = Material(Color(0.1, 0.1, 0.1), Color(0.6, 0.6, 0.6), Color.white(), 100, earth_tex)

    objects = [Sphere(Vector3(0, 0, -1), Vector3.zeros(), 1, mat), Plane(Vector3(0, -1, 0), Vector3.zeros(), mat)]

    """Calculate the aspect ratio of the view plane based on the background image"""
    height, width, channels = back.shape

    aspect_ratio = float(width) / height
    screen = (-1, 1 / aspect_ratio, 1, -1 / aspect_ratio)  # left, top, right, bottom

    image = back

    """ For every pixel along a view plane shoot a ray and trace back the color"""
    for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
        for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
            pixel = Vector3(x, y, 0)

            # Define primary ray
            primary_ray = Ray(camera.position, Vector3.normalize(Vector3.subtract(pixel, camera.position)))

            # Check for ray object intersection and get the closest intersection point
            t, obj = closest_intersection(primary_ray, objects)

            if not obj:
                continue

            # Get the color of the object at the specific location
            intersection = Vector3.add(primary_ray.origin, Vector3.scalar_mul(t, primary_ray.direction))
            col = obj.color(light, camera.position, intersection)

            # Get the direction vector from intersection point to a light source
            shifted_point = Vector3.add(intersection, Vector3.scalar_mul(1E-5, obj.normal(intersection)))
            light_direction = Vector3.normalize(Vector3.subtract(light.position, shifted_point))

            # Soft shadows
            perpL = Vector3.cross(light_direction, Vector3(0, 1, 0))

            if perpL.x == 0.0 and perpL.y == 0.0 and perpL.z == 0.0:
                perpL.x = 1

            # Get the vector that points in the direction of a light's edge
            light_edge = Vector3.normalize(
                Vector3.subtract(Vector3.add(Vector3.scalar_mul(light.radius, perpL), light.position),
                                 intersection))

            # Get an angle of a cone from intersection point to a light source
            cone_angle = math.acos(Vector3.dot(light_direction, light_edge)) * 2.0

            # Get the averaged color of all the shadow rays
            shadow_col = soft_shadow([light_sample(light_direction, cone_angle) for i in range(16)], objects, light,
                                     shifted_point)

            # Get the resulting color with shadow
            col = Color.subtract(col, Color(shadow_col, shadow_col, shadow_col))
            
            image[i, j] = (col.r * 255, col.g * 255, col.b * 255)

    plt.imsave(os.path.join(RESULTS_PATH, 'image2.png'), image)


if __name__ == '__main__':
    main()
