from setuptools import setup, find_packages

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.readlines()

with open("requirements_dev.txt") as requirements_file:
    requirements_dev = requirements_file.readlines()

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    # Info
    author="Luca Bonfiglioli",
    author_email="Luca.Bonfiglioli@gmail.com",
    name="rsg",
    description="Random Structure Generator",
    long_description=readme,
    license="GNU General Public License v3.0",
    version="0.0.0",
    keywords="choixe",
    url="https://github.com/lucabonfiglioli/rsg",
    # Requirements
    python_requires=">=3.9",
    install_requires=requirements,
    # Tests
    test_suite="tests",
    test_requires=requirements_dev,
    # Packaging
    packages=find_packages(include=["rsg", "rsg.*"]),
    include_package_data=True,
)
