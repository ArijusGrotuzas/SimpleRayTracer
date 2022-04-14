# Description
A naive implementation of a simple raytracer that renders basic shapes in Python.

## Tabel of contents
- [Sphere intersection](#Sphere-ray-intersection)
- [Plane intersection](#Plane-ray-intersection)
- [Spherical texture mapping](#Spherical-texture-mapping)
- [Soft shadows](#Soft-shadows)

## Sphere-ray intersection

The definition of the a sphere is given by:

![sphere](https://latex.codecogs.com/svg.image?\left\|&space;x&space;-&space;c\right\|&space;=&space;r)

where `x` is an arbitrary point on a sphere, `c` is a center of the sphere and `r` is the radius. Since `x` is a point on a sphere, we can substitute it with a ray definition:

![ray-sphere](https://latex.codecogs.com/svg.image?\left\|&space;o&space;&plus;&space;dt&space;-&space;c\right\|^2&space;=&space;r^2)

where `o` is the origin of the ray, `d` is a unit vector that describes the direction of the ray, and `t` is a scalar that describes a point along the ray. If we solve for `t` we get:

![a](https://latex.codecogs.com/svg.image?a&space;=&space;\left\|&space;d\right\|^2&space;=&space;1)

![b](https://latex.codecogs.com/svg.latex?b%20=%202d%20\cdot%20(o%20-%20c))

![c](https://latex.codecogs.com/svg.latex?c%20=%20\left\|%20o%20-%20c\right\|^2%20-%20r^2)

![discriminant](https://latex.codecogs.com/svg.image?\Delta&space;=&space;b^2&space;-&space;4ac)

If we compute the discriminant![delta](https://latex.codecogs.com/svg.image?\Delta) we can determine if the ray intersects the sphere, a positive ![delta](https://latex.codecogs.com/svg.image?\Delta) means that the ray intersects the sphere, otherwise the ray misses the sphere. Since `d` is a unit vector we do not need to compute `a`. Furthermore, we can also derive a point of intersection by calculating coefficients `x1` and `x2`.

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

We can define a plane by a surface normal vector `n`, which describes plane's orientation, and a point on a plane `p`, which describes its translation. If we take an arbitrary point `x`, then the `distance` between the point and the plane is defined as follows:

![distance](https://latex.codecogs.com/svg.image?distance&space;=&space;\left\|&space;(x&space;-&space;s)&space;\cdot&space;n&space;\right\|)

When `distance = 0` that means point `x` resides on the plane. We can substitute point `x` with a ray definition, and set the distance equal to 0, to get the following formula:

![intersection](https://latex.codecogs.com/svg.image?\left&space;(&space;o&space;&plus;&space;dt&space;-&space;s\right&space;)&space;\cdot&space;n&space;=&space;0)

since the distance is set to 0 the absolute value becomes irrelevant. If we solve for `t` we get the following:

![dr](https://latex.codecogs.com/svg.image?t&space;=&space;\frac{\left&space;(&space;s&space;-&space;o&space;\right&space;)&space;\cdot&space;n}{d&space;\cdot&space;n})

this will give us the point of intersection on the plane. However if the angle is perpendicular to the ray direction, the resulting formula would give us division by a zero, therefore we can first find the angle between the plane normal and the direction of the ray.

>`Python example`

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

To texture a sphere, we can derive latitude ![phi](https://latex.codecogs.com/svg.image?\phi) and longitude ![theta](https://latex.codecogs.com/svg.image?\theta) of a 3D point on a sphere, and then use these values as `u` and `v` texture coordinates. To do so we need to define two unit-length vectors `Vn` and `Ve` that point in the direction of the north pole and the equator, the vectors can have arbitrary directions, however, the mapping will depend on their direction. We then find the unit-length vector `Vp`, which points from the center of the sphere to the point we are coloring. Since the dot-product of two unit-length vectors is equal to a `cosine` of an angle between them, we can simply find the latitude as follows:

![latitude](https://latex.codecogs.com/svg.image?\phi&space;=&space;\arccos{(V_n&space;\cdot&space;V_p)})

We can derive longitude the same way, additionaly we also need to divide the angle between the `Ve` and `Vp` by ![phi](https://latex.codecogs.com/svg.image?\phi):

![longitude](https://latex.codecogs.com/svg.image?\theta&space;=&space;\frac{\arccos{(V_p&space;\cdot&space;V_e)}}{\sin(\phi)}&space;\cdot&space;\frac{1}{2\pi}&space;)

We can also divide the angle by ![2pi](https://latex.codecogs.com/svg.image?2\pi) to convert `u` to the range from 0 to 0.5, since ![theta](https://latex.codecogs.com/svg.image?\theta) ranges from 0 to ![positivepi](https://latex.codecogs.com/svg.image?\pi), and since the dot-product cannot tell us on which side of equator vector `Ve` the point is, we can derive a new vector, orthogonal to the vectors `Ve` and `Vn` and check the angle between it and the vector `Vp`:

![bl](https://latex.codecogs.com/svg.image?\alpha&space;=&space;V_p&space;\cdot&space;(V_n&space;\times&space;V_e))

We then use the angle ![alpha](https://latex.codecogs.com/svg.image?\alpha) to get the texture coordinate `u`:

![piecewise](https://user-images.githubusercontent.com/50104866/163346416-065b5a6c-dc28-4a4f-83b7-49d3f40f168e.png)

>`Example image`

![alt text](https://github.com/ArijusGrotuzas/SimpleRayTracer/blob/main/results/combined/image.png)

>`Python example`

```Python
# Returns a u, v coordinates given a point on a sphere
def spherical_map(self, intersection):
    
    # Define vectors Vn and Ve
    pole = Vector3(0, 1, 0)
    equator = Vector3(-1, 0, 0)

    # Get vector Vp
    normal = self.normal(intersection)
    
    # Get the angle between V_n and V_p
    phi = math.acos(Vector3.dot(pole, normal))
    v = phi / math.pi

    theta = (math.acos(Vector3.dot(equator, normal) / math.sin(phi))) / (2 * math.pi)

    if Vector3.dot(normal, Vector3.cross(pole, equator)) > 0:
        u = theta
    else:
        u = 1 - theta

    return u, v
```

## Soft shadows
>`16 shadow spp`

![alt text](https://github.com/ArijusGrotuzas/SimpleRayTracer/blob/main/results/shadow/shadow_mask.png)
