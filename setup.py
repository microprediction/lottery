import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="lottery",
    version="0.0.1",
    description="Lottery like mechanisms",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/microprediction/lottery",
    author="microprediction",
    author_email="pcotton@intechinvestments.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["lottery"],
    test_suite='pytest',
    tests_require=['pytest'],
    include_package_data=True,
    install_requires=["wheel","pathlib"],
    entry_points={
        "console_scripts": [
            "lottery=lottery.__main__:main",
        ]
    },
)
