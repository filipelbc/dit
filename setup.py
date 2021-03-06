# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='dit',
    version='0.7.3',

    description='A CLI work time tracking tool.',

    url='https://github.com/filipelbc/dit',

    author='Filipe L B Correia',
    author_email='filipelbc@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='timetable clocking',

    packages=['dit'],

    install_requires=['tzlocal'],

    extras_require={
        'dev': [],
        'test': [],
    },

    package_data={
        'dit': ['command_info.json'],
    },

    entry_points={
        'console_scripts': ['dit=dit:main',
                            'dit-completion=dit:completion'],
    },
)
