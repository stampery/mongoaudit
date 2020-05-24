# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from mongoaudit.version import __version__

with open('README.rsc') as f:
    readme = f.read()

setup(
    name='mongoaudit',
    version=__version__,
    description='An automated pentesting tool that lets you know if your MongoDB instances are properly secured',
    long_description=readme,
    author='Stampery Inc.',
    author_email='info@stampery.com',
    url='https://github.com/stampery/mongoaudit',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
          'mongoaudit = mongoaudit.__main__:main'
        ]
    },
    install_requires=[
        'pymongo>=3.9.0',
        'urwid>=1.3.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        'Topic :: Security',
        'Topic :: System :: Systems Administration'
    ]
)
