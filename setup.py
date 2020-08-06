#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open('README.md', 'r') as fp:
    long_description = fp.read()
    pos = long_description.find('# Development')
    if pos > -1:
        long_description = long_description[:pos]

setuptools.setup(
    name='qri',
    version='0.1.1',
    author='Dustin Long',
    author_email='dustmop@qri.io',
    description='qri python client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/qri-io/qri-python',
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas==1.0.0',
        'Markdown==3.2.2'
    ],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6'
)
