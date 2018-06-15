#!/usr/bin/env python
import io
import ast
import os.path
from setuptools import setup, find_packages

def get_version_tuple():
    init_py = os.path.join(os.path.dirname(__file__), 'trio_mysql', '__init__.py')
    with open(init_py) as f:
        for line in f:
            before, sep, version = line.rpartition('VERSION = ')
            if sep and not before:
                return ast.literal_eval(version)
        else:
            raise ValueError('Version not found')
version_tuple = get_version_tuple()

if version_tuple[3] is not None:
    version = "%d.%d.%d_%s" % version_tuple
else:
    version = "%d.%d.%d" % version_tuple[:3]

with io.open('./README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="trio_mysql",
    version=version,
    url='https://github.com/python-trio/trio-mysql/',
    author='Matthias Urlichs',
    author_email='matthias@urlichs.de',
    description='Pure Python MySQL Driver',
    long_description=readme,
    license="MIT",
    install_requires=[
        "trio",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Database',
        'Framework :: Trio',
    ],
)
