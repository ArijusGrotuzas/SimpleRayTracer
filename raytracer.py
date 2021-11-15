""" For navigating system files """
import os
import random
import subprocess

import matplotlib.pyplot as plt  # For saving images
import numpy as np  # For converting textures into arrays
from PIL import Image  # For opening images

from definitions import TEXTURES_PATH, RESULTS_PATH, FILEBROWSER_PATH
from objects import *


# Opens windows explorer's path
def explore(path):
    # explorer would choke on forward slashes
    path = os.path.normpath(path)

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])


# Clears console
def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


# Convert degrees to radians
def deg2rad(degree):
    return (degree * math.pi) / 180


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
            samples_sum += 1
        else:
            samples_sum += 2

    try:
        return (samples_sum / len(samples)) - 1
    except ZeroDivisionError:
        return 0


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

    mat = Matrix4X4.rotationMat(angle, axis)

    return Matrix4X4.mulVector3(mat, Vector3(x, y, z))


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


def test():
    rot = Matrix4X4.rotationMat(deg2rad(-90), Vector3(1, 0, 0))
    print(repr(rot), "\n")

    translate = Matrix4X4.translationMat(Vector3(0, 1, 0))
    print(repr(translate), "\n")

    combined = Matrix4X4.mulMat(translate, rot)
    print(repr(combined), "\n")


def main():
    """Import the textures"""
    earth_texture = Image.open(os.path.join(TEXTURES_PATH, 'earth.jpg'))
    earth_tex = np.asarray(earth_texture)

    background = Image.open(os.path.join(TEXTURES_PATH, 'test.jpg'))
    back = np.asarray(background)

    """Define objects present in the scene"""
    height, width, channels = back.shape
    camera = Camera(Vector3(0, 0, 1.5), Vector3(0, deg2rad(0), 0), width, height, 1)

    print(repr(camera.modelMat), "\n")

    light = PointLight(Vector3(5, 5, 5), Vector3.zeros(), 1, Color(1, 1, 1), Color(0.945, 0.703, 0.253),
                       Color(0.945, 0.703, 0.253))

    mat = Material(Color(0.1, 0.1, 0.1), Color(0.6, 0.6, 0.6), Color.white(), 100, earth_tex)

    objects = [Sphere(Vector3(0, 0, 0), Vector3(0, deg2rad(250), 0), 1, mat),
               Plane(Vector3(0, -1, 0), Vector3.zeros(), mat)]

    shadow_texture = np.ones((height, width, 3), np.uint8)
    shadow_texture.fill(255)
    image = np.copy(back)
    image.flags.writeable = True

    """ For every pixel along a view plane shoot a ray and trace back the color"""
    for i, y in enumerate(np.linspace(camera.top.y, camera.bottom.y, height)):
        for j, x in enumerate(np.linspace(camera.left.x, camera.right.x, width)):
            pixel = Matrix4X4.mulVector3(camera.modelMat, Vector3(x, y, -0.5))

            # Define primary ray
            primary_ray = Ray(camera.center, Vector3.normalize(Vector3.subtract(pixel, camera.center)))

            # Check for ray object intersection and get the closest intersection point
            t, obj = closest_intersection(primary_ray, objects)

            if not obj:
                continue

            # Get the color of the object at the specific location
            intersection = Vector3.add(primary_ray.origin, Vector3.scalar_mul(t, primary_ray.direction))
            col = obj.color(light, camera.center, intersection)

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
            shadow_col = soft_shadow([light_sample(light_direction, cone_angle) for i in range(36)], objects, light,
                                     shifted_point)

            # Write to the shadow texture
            shadow_intensity = shadow_col * 255
            shadow_texture[i, j] = (shadow_intensity, shadow_intensity, shadow_intensity)

            # Get the resulting color with shadow
            col = Color.multiply(col, Color(shadow_col, shadow_col, shadow_col))

            image[i, j] = (col.r * 255, col.g * 255, col.b * 255)

        # print("progress: %d/%d" % (i + 1, height))
        # clearConsole()

    plt.imsave(os.path.join(RESULTS_PATH, 'combined\\image3.png'), image)
    plt.imsave(os.path.join(RESULTS_PATH, 'shadow\\shadow_mask.png'), shadow_texture)
    print(f'Saved to {os.path.join(RESULTS_PATH, "image3.png")}')
    explore(RESULTS_PATH)


if __name__ == '__main__':
    main()
