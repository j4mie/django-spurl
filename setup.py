from setuptools import setup, find_packages

description = 'A Django template library for manipulating URLs.'

setup(
    name='django-spurl',
    version='0.1',
    description=description,
    long_description=description,
    author='Jamie Matthews',
    author_email='jamie.matthews@gmail.com',
    url='http://github.com/j4mie/django-spurl/',
    packages=find_packages(),
    install_requires=['urlobject==0.5.1'],
)
