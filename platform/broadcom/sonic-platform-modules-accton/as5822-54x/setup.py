#!/usr/bin/env python

import os
import sys
from setuptools import setup
os.listdir

setup(
   name='as5822_54x',
   version='1.0',
   description='Module to initialize Accton AS5822-54X platforms',
   
   packages=['as5822_54x'],
   package_dir={'as5822_54x': 'as5822-54x/classes'},
)

