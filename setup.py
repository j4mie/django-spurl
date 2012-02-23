import os
import re
from setuptools import setup, find_packages

description = 'A Django template library for manipulating URLs.'

rel_file = lambda *args: os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

def read_from(filename):
    fp = open(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def get_version():
    data = read_from(rel_file('spurl', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", data).group(1)

setup(
    name='django-spurl',
    version=get_version(),
    description=description,
    long_description=description,
    author='Jamie Matthews',
    author_email='jamie.matthews@gmail.com',
    url='http://github.com/j4mie/django-spurl/',
    packages=find_packages(),
    install_requires=['urlobject>=2.0.0'],
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Framework :: Django',
        'Operating System :: OS Independent',
    ]
)
