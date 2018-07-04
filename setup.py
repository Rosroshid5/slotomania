#!/usr/bin/env python

from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='slotomania',
    version='0.0.13',
    description='Slotomania',
    long_description=long_description,
    scripts=["bin/sloto.py"],
    url='https://github.com/conanfanli/slotomania',
    packages=find_packages(exclude=['tests*']),
    install_requires=['yapf>=0.21'],
    python_requires='~=3.6',
    extras_require={'dev': ['ipython', 'mypy']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='slotomania',
    author='Conan Li',
    author_email='conanlics@gmail.com',
    license='MIT',
)
