# -*- coding:utf-8 -*-
'''
Created on 22/03/2010

@author: fccoelho
'''

from ez_setup import use_setuptools
use_setuptools()
#from distutils.core import setup
#from distutils.extension import Extension
from setuptools import setup, find_packages


setup(name='liveplots', 
        version  = '0.1.0', 
        author = 'Flavio Codeco Coelho', 
        author_email = 'fccoelho@gmail.com', 
        url = 'http://code.google.com/p/liveplots/',
        description = 'Real-time live plot server',
        zip_safe = True,
        packages = find_packages(),
        install_requires = ["numpy >= 1.2"], 
        test_suite = 'nose.collector', 
        license = 'GPL',  
      )
