# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='mongoaudit',
    version='0.0.1',
    description='An automated pentesting tool that lets you know if your MongoDB instances are properly secured',
    long_description=readme,
    author='Stampery Inc.',
    author_email='info@stampery.com',
    url='https://github.com/stampery/mongoaudit',
    license=license,
    packages=[
      'mongoaudit'
    ],
    package_dir={
      'mongoaudit': 'src'
    },
    entry_points={
      'console_scripts': [
          'mongoaudit = mongoaudit.main:main'
      ]
    }
)
