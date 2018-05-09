#!/usr/bin/env python

import os
import re
import sys
import codecs

from setuptools import setup, find_packages

def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")

setup(
    name='django-spurl',
    version=find_version('spurl', '__init__.py'),
    license='Public Domain',

    install_requires=[
        'urlobject>=2.4.0',
        'six',
    ],
    setup_requires=[
        'urlobject>=2.4.0',
        'django>=1.4',
        'nose',
        'six',
    ],

    description='A Django template library for manipulating URLs.',
    long_description=read('README.md') + '\n\n' + read('CHANGES'),

    author='Jamie Matthews',
    author_email='jamie.matthews@gmail.com',

    maintainer='Basil Shubin',
    maintainer_email='basil.shubin@gmail.com',

    url='http://github.com/j4mie/django-spurl',
    download_url='https://github.com/j4mie/django-spurl/zipball/master',
    
    packages=find_packages(exclude=('example*', '*.tests*')),
    include_package_data=True,

    test_suite='nose.collector',
    tests_require=['nose'],

    zip_safe=False,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
