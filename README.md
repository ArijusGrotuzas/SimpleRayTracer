# Description
Simple raytracer that renders basic shapes in Python.

# Tabel of contents
- [Sphere intersection](#Sphere-ray-intersection)
- [Plane intersection](#Plane-ray-intersection)
- [Spherical texture mapping](#Spherical-texture-mapping)
- [Soft shadows](#Soft-shadows)

## Sphere-ray intersection

```Python
# Calculates intersection between a sphere and a ray
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
```

## Plane-ray intersection

```Python
# Calculates intersection with an infinite plane
def calculate_intersection(self, ray):
    denominator = Vector3.dot(Vector3.normalize(ray.direction), self.surface_normal)

        if abs(denominator) > 1E-5:
            t = Vector3.dot(Vector3.subtract(self.position, ray.origin), self.surface_normal) / denominator

            if t >= 0:
                return t

        return None
```
## Spherical texture mapping
```Python
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
```
![alt text](https://github.com/ArijusGrotuzas/SimpleRayTracer/blob/main/results/image.png)

## Soft shadows
>`16 shadow spp`

![alt text](https://github.com/ArijusGrotuzas/SimpleRayTracer/blob/main/results/image2.png)
