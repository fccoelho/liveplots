# -*- coding:utf-8 -*-
'''
Created on 22/03/2010

@author: fccoelho
'''
from __future__ import absolute_import



from setuptools import setup, find_packages

setup(name='liveplots',
      version='0.8.3',
      author='Flávio Codeço Coelho',
      author_email='fccoelho@gmail.com',
      url='https://github.com/fccoelho/liveplots',
      description='Real-time live plot server',
      zip_safe=True,
      packages=find_packages(),
      install_requires=["numpy >= 1.2", "pyinotify >= 0.8.9"],
      test_suite='nose.collector',
      license='GPL',
      )
