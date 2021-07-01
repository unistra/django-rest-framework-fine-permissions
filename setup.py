#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages


with open('README.rst') as readme:
    long_description = readme.read()


with open('requirements.txt') as requirements:
    lines = requirements.readlines()
    libraries = [lib for lib in lines if not lib.startswith('-')]
    dependency_links = [link.split()[1] for link in lines if
        link.startswith('-f')]


setup(
    name='djangorestframework-fine-permissions',
    version='0.9.0',
    packages=find_packages(exclude=["tests*"]),
    install_requires=libraries,
    dependency_links=dependency_links,
    include_package_data=True,
    long_description=long_description,
    author='Arnaud Grausem',
    author_email='arnaud.grausem@unistra.fr',
    maintainer='Arnaud Grausem',
    maintainer_email='arnaud.grausem@unistra.fr',
    description='Field level permissions for Django REST Framework',
    keywords=['django', 'REST', 'rest_framework', 'permissions'],
    url='https://github.com/unistra/django-rest-framework-fine-permissions',
    download_url='https://pypi.python.org/pypi/djangorestframework-fine-permissions',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.2',
    ]
)
