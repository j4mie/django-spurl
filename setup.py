import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

from spurl import __version__

setup(
    name='django-spurl',
    version=__version__,
    packages=find_packages(exclude=['example']),
    include_package_data=True,
    license='Public Domain',
    description='A Django template library for manipulating URLs.',
    long_description=README,
    url='http://github.com/j4mie/django-spurl',
    author='Jamie Matthews',
    author_email='jamie.matthews@gmail.com',
    maintainer='Basil Shubin',
    maintainer_email='basil.shubin@gmail.com',
    install_requires=[
        'urlobject>=2.0.0',
        'six',
    ],
    setup_requires=[
        'urlobject>=2.0.0',
        'django>=1.3',
        'nose',
        'six',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
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
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    zip_safe=False,
)
