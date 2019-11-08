# -*- coding:utf-8 -*-
'''
Created on 22/03/2010

@author: fccoelho
'''
from __future__ import absolute_import

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(name='liveplots',
      version='0.9.0',
      author='Flávio Codeço Coelho',
      author_email='fccoelho@gmail.com',
      url='https://github.com/fccoelho/liveplots',
      description='Real-time live plot server',
      long_description=long_description,
      zip_safe=True,
      packages=find_packages(),
      install_requires=["numpy >= 1.2"],
      test_suite='nose.collector',
      license='GPL',
      )
