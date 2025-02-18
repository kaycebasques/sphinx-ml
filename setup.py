import json
import os
import setuptools


cwd = os.path.abspath(os.path.dirname(__file__))
with open(f'{cwd}/sphinx-ml/version.json', 'r') as f:
    version = json.load(f)['version']


def install_requires():
    with open('requirements.txt', 'r') as f:
        return [line.strip() for line in f.readlines()]


setuptools.setup(
    name='sphinx-ml',
    version=version,
    packages=['sphinx-ml'],
    package_data={
        'sphinx-ml': ['version.json']
    },
    install_requires=install_requires(),
    classifiers=[],
)
