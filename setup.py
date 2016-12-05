from setuptools import (
    find_packages,
    setup,
)

import load

requirements = [
    'locustio==0.7.3',
]

setup(
    name='load-tests',
    version=load.__version__,
    description='load tests',
    packages=find_packages(),
    install_requires=requirements,
)
