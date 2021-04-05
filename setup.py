#!/usr/bin/env python

import setuptools

from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(name='pymkup',
      description='Python library to process Revu PDFs',
      long_description=long_description,
      long_description_content_type='text/markdown',
      version='0.1',
      license="MIT",
      classifiers = [
         "Topic :: Office/Business",
         "Development Status :: 4 - Beta",
         "Intended Audience :: Developers",
         "License :: OSI Approved :: MIT License",
         "Programming Language :: Python :: 3"
      ],
      url='https://github.com/psolin/pymkup',
      author='Paul Solin',
      author_email='paulsolin@gmail.com',
)