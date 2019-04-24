#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

setup(
    name='nofollow_finder',
    description='Python command line tool that detects nofollow '
                'links to specified web pages.',
    version='1.3.0',
    url='https://github.com/frnhr/nofollow_finder',
    author='Fran Hrzenjak',
    author_email='fran@changeset.hr',
    scripts=['bin/nofollow_finder'],
    packages=['nofollow_finder'],
    license='MIT',
    keywords='',
    install_requires=[
        'docopt>=0.6.2,<0.7',
        'pyquery>=1.4.0,<1.5',
        'lxml>=4.2.5,<4.3',
        'subprocess32>=3.5.3,<4',
        'python-dotenv>=0.10.1,<0.11',
    ],
    extras_require={
        'dev': [
            'mock>=2.0.0,<3',
        ],
    },
)
