import setuptools
import unittest


def cli_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="docker-stack-deploy",
    scripts=['bin/docker-sdp'],
    version="0.1.0",
    author="NeuroForge GmbH & Co. KG",
    author_email="kontakt@neuroforge.de",
    description="docker-stack-deploy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://neuroforge.de/",
    package_data={ "docker-stack-deploy": ["py.typed"] },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    test_suite='setup.cli_test_suite',
    python_requires='>=3.8',
    install_requires=[
        "pyyaml",
        "mypy>=0.800"
    ],
    extras_require={
        'dev': []
    }
)