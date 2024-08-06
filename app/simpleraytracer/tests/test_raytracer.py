import unittest

from ..src.raytracer import *


class RaytracerTest(unittest.TestCase):
    def test_closest_intersection(self):
        mat = Material(Color.white(), Color.white(), Color.white(), 100)
        sphere_first = Sphere(Vector3(0, 0, 35), Vector3.zeros(), 5, mat)
        sphere_second = Sphere(Vector3(0, 0, 65), Vector3.zeros(), 10, mat)

        distance, obj = __find_closest_intersection(Ray(Vector3.zeros(), Vector3(0, 0, 1)), [sphere_first, sphere_second])

        self.assertEqual(30.0, distance)
        self.assertEqual(sphere_first, obj)

    def test_calculate_soft_shadow(self):
        # The light is placed at (5, 20, 0) with a radius of 2, the sphere is sitting under it at (5, 10, 0)
        # with a radius of 2.
        spheres = [Sphere(Vector3(5, 10, 0), Vector3.zeros(), 2, Material())]
        samples = [Vector3(i, 20, 0) for i in np.linspace(4, 6, 100)]

        shadow_value = __calculate_soft_shadow(samples, spheres, Vector3(5, 20, 0), Vector3(38.1, 0, 0))

        self.assertEqual(0.5, shadow_value)
