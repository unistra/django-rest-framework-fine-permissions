#!/usr/bin/env python

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
    version='0.9.2',
    packages=find_packages(exclude=["tests*"]),
    install_requires=libraries,
    dependency_links=dependency_links,
    include_package_data=True,
    long_description=long_description,
    author='dnum-dip-unistra',
    author_email='dnum-dip@unistra.fr',
    maintainer='dnum-dip-unistra',
    maintainer_email='dnum-dip@unistra.fr',
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        'Framework :: Django',
        'Framework :: Django :: 5.2',
    ]
)
