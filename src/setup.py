# -*- coding:utf-8 -*-
'''
Created on 22/03/2010

@author: fccoelho
'''

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages


setup(name='liveplots', 
        version  = '0.3', 
        author = 'Flavio Codeco Coelho', 
        author_email = 'fccoelho@gmail.com', 
        url = 'http://code.google.com/p/liveplots/',
        description = 'Real-time live plot server',
        zip_safe = True,
        packages = find_packages(),
        install_requires = ["numpy >= 1.2","pyinotify >= 0.8.9"], 
        test_suite = 'nose.collector', 
        license = 'GPL',  
      )
