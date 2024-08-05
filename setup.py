from setuptools import find_packages, setup

VERSION = '0.0.10'
DESCRIPTION = 'Simple ray tracer'
LONG_DESCRIPTION = 'Simple ray tracer'

setup(
    name="simple-raytracer",
    version=VERSION,
    description=DESCRIPTION,
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=LONG_DESCRIPTION,
    url="",
    author="",
    author_email="",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy"],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    python_requires=">=3.10",
)
