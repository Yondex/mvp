#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages
# from codecs import open
import io
from os import path



here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with io.open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='MVP',
    version=1.0,
    description='Magic Power',
    long_description=long_description,
    url='https://github.com/Yondex/mvp',
    author='Ran Aroussi',
    author_email='inc238@gmail.com',
    license='Apache',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',


        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    platforms=['any'],
    keywords='pandas, yahoo finance, pandas datareader',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'examples']),
    install_requires=['pandas>=0.24', 'numpy>=1.15',
                      'requests>=2.20', 'multitasking>=0.0.7',
                      'lxml>=4.5.1'],
    entry_points={
        'console_scripts': [
            'sample=sample:main',
        ],
    },
)