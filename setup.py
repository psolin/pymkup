import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pymkup",
    version="0.6",
    description="Accessing Bluebeam Revu PDF Data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/psolin/pymkup",
    author="Paul Solin",
    author_email="paulsolin@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["pymkup"],
    include_package_data=True,
    install_requires=["pdfreader", "matplotlib"]
)
