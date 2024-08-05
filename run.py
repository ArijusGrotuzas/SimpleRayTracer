import os

import matplotlib.pyplot as plt  # For saving images
from PIL import Image  # For opening images
from simpleraytracer import *


def main():
    texture_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")  # Textures path

    earth_texture = Image.open(os.path.join(texture_path, 'earth.jpg'))
    earth_tex = np.asarray(earth_texture)

    """Define objects present in the scene"""
    height, width = 125, 125
    camera = Camera(Vector3(0, 0, 1.5), Vector3.zeros(), width, height, 1)

    light = PointLight(
        Vector3(5, 5, 5),
        Vector3.zeros(),
        1,
        Color(1, 1, 1),
        Color(0.945, 0.703, 0.253),
        Color(0.945, 0.703, 0.253)
    )

    mat = Material(
        Color(0.1, 0.1, 0.1),
        Color(0.6, 0.6, 0.6),
        Color.white(),
        100,
        earth_tex
    )

    objects = [
        Sphere(Vector3(0, 0, 0), Vector3.zeros(), 1, mat),
        Plane(Vector3(0, -1, 0), Vector3.zeros(), mat)
    ]

    image = render(objects, light, camera)

    plt.imshow(image, interpolation='nearest')
    plt.show()


if __name__ == '__main__':
    main()
