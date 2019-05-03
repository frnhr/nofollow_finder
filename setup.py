#!/usr/bin/env python
# coding=utf-8
import os

from setuptools import setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('nofollow_finder')


setup(
    name='nofollow_finder',
    description='Python command line tool that detects nofollow '
                'links to specified web pages.',
    version='1.4.0',
    url='https://github.com/frnhr/nofollow_finder',
    author='Fran Hrzenjak',
    author_email='fran@changeset.hr',
    scripts=['bin/nofollow_finder'],
    packages=['nofollow_finder'],
    package_data={'': extra_files},
    license='MIT',
    keywords='',
    install_requires=[
        'docopt>=0.6.2,<0.7',
        'pyquery>=1.4.0,<1.5',
        'lxml>=4.2.5,<4.3',
        'subprocess32>=3.5.3,<4',
        'python-dotenv>=0.10.1,<0.11',
        'requests>=2.21.0,<2.22',
    ],
    extras_require={
        'dev': [
            'mock>=2.0.0,<3',
        ],
    },
)
