from setuptools import setup

setup(
    name='dit',
    version='0.7dev',

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

    keywords='clocking todo',

    packages=['dit'],

    install_requires=['tzlocal'],

    extras_require={
        'dev': [],
        'test': [],
    },

    package_data={
        'dit': [],
    },

    entry_points={
        'console_scripts': ['dit=dit.dit:main',
                            'dit-completion=dit.dit:completion'],
    },
)
