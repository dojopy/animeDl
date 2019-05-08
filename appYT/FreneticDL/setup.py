#coding:utf-8

import os
from setuptools import find_packages, setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='FreneticDL',
    version='1.0.0',
    author='Henry Cristofer Vasquez Conde',
    author_email='cristofer_dev.py@hotmail.com',
    description=('Potente CLI(interfaz de línea de comandos) atractiva \
        para descargar archivos utilizando segmentacion y multithreading.'),
    long_description=open('README.md').read(),
    license='MIT',
    keywords='FreneticDL utilities download',
    url='',
    packages=find_packages(),
    package_data={
        'FreneticDL': ['*.txt']
    },
    install_requires=[required],
    classifiers=[
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: MIT',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        "Operating System :: POSIX",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",

    ]
)