# Description
Simple raytracer that renders basic shapes in Python.

# Tabel of contents
- [Sphere intersection](#Sphere-ray-intersection)
- [Plane intersection](#Plane-ray-intersection)
- [Spherical texture mapping](#Spherical-texture-mapping)
- [Soft shadows](#Soft-shadows)

## Sphere-ray intersection

The definition of the a sphere is given by:

![sphere](https://latex.codecogs.com/svg.image?\left\|&space;x&space;-&space;c\right\|&space;=&space;r)

where `x` is an arbitrary point on a sphere, `c` is a center of the sphere and `r` is the radius. Since `x` is a point on a sphere, we can substitute with a ray definition:

![ray-sphere](https://latex.codecogs.com/svg.image?\left\|&space;o&space;&plus;&space;dt&space;-&space;c\right\|^2&space;=&space;r^2)

where `o` is the origin of the ray, `d` is a unit vector that describes direction of the ray, and `t` is a scalar that describes a point along the ray. If we solve for `t` we get:

![a](https://latex.codecogs.com/svg.image?a&space;=&space;\left\|&space;d\right\|^2&space;=&space;1)

![b](https://latex.codecogs.com/svg.latex?b%20=%202d%20\cdot%20(o%20-%20c))

![c](https://latex.codecogs.com/svg.latex?c%20=%20\left\|%20o%20-%20c\right\|^2%20-%20r^2)

![discriminant](https://latex.codecogs.com/svg.image?\Delta&space;=&space;b^2&space;-&space;4ac)

If we compute the discriminant ![delta](https://latex.codecogs.com/svg.image?\Delta) we can determine if the ray intersects the sphere, a positive ![delta](https://latex.codecogs.com/svg.image?\Delta) means that ray intersects the sphere, otherwise the ray misses the sphere. Since `d` is a unit vector we do not need to compute `a`. Furthermore, we can also derive a point of intersection by calculating coefficients `x1` and `x2`.

>`Python example`

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
![alt text](https://github.com/ArijusGrotuzas/SimpleRayTracer/blob/main/results/combined/image.png)

## Soft shadows
>`16 shadow spp`

![alt text](https://github.com/ArijusGrotuzas/SimpleRayTracer/blob/main/results/shadow/shadow_mask.png)
