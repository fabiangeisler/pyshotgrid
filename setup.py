#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['git+git://github.com/shotgunsoftware/python-api.git@v3.3.1']

test_requirements = [ ]

setup(
    author="Fabian Geisler",
    author_email='info@fasbue.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="OOP for Autodesk ShotGrid",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pyshotgrid',
    name='pyshotgrid',
    packages=find_packages(where='./src'),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/fabiangeisler/pyshotgrid',
    version='0.1.0',
    zip_safe=False,
)
