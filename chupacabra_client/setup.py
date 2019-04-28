import os
import re

from setuptools import find_packages, setup


def get_init_path() -> str:
    """Get the path to __init__.py"""
    current_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(current_dir, 'chupacabra_client', '__init__.py')


def extract_variable_name(variable_name: str) -> str:
    """Get a variable from the __init__.py file"""
    path = get_init_path()
    name = None
    with open(path) as f:
        for line in f:
            if line.startswith(variable_name):
                matches = re.findall(r'["\']([^"\']+)["\']', line)
                if len(matches) != 1:
                    raise AssertionError('{} line not correctly formed.'.format(variable_name))
                name = matches[0]
                break

    if name is None:
        raise AssertionError('{} not found.'.format(variable_name))
    return name

setup(
    name=extract_variable_name('__name__'),
    version=extract_variable_name('__version__'),
    packages=find_packages(),
    install_requires=[
        "grpcio >= 1.19",
        "grpcio-tools >= 1.19",
        "protobuf >= 3.6.1"
    ]
)