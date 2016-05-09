from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dvb',

    version='1.1',

    description='query Dresden\'s public transport system for current \
bus- and tramstop data in python',
    long_description=long_description,
    url='https://github.com/kiliankoe/dvbpy',
    author='kiliankoe',
    author_email='me@kilian.io',
    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='dvb vvo tram bus public transport dresden',
    packages=find_packages(),

    install_requires=['requests==2.5.0', 'pyproj'],
)
