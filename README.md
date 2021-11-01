# Description
Simple raytracer that renders basic shapes in Python.

# Tabel of contents
- [Sphere intersection](#Sphere-ray-intersection)
- [Plane intersection](#Plane-ray-intersection)
- [Example](#Example)

## Sphere-ray intersection

> `Example`

```Python
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
```

## Plane-ray intersection

>`Example`

```Python
# Calculates intersection with an infinite plane
    def intersect(self, ray_origin, ray_direction):
        denominator = np.dot(normalize(ray_direction), self.normal)

        if abs(denominator) > 0.0001:
            t = np.dot(self.center - ray_origin, self.normal) / denominator

            if t >= 0:
                return t

        return None
```

## Example
![alt text](https://github.com/ArijusGrotuzas/SimpleRayTracer/blob/main/image.png)
