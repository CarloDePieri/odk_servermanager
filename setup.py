import io
import re
from setuptools import setup

setup(
        name='arma_keysmanager',
        version='0.1',
        packages=['arma_keysmanager'],
        include_package_data=True,
        license='GPLv3',
        author='Carlo De Pieri',
        description='Quickly set up keys in an arma server',
        install_requires=[
            'beautifulsoup4==4.8.2'
            ],
        extras_require={
            'dev': [
                'pytest>=4.0.0',
                'pytest-sugar>=0.9.2',
                ]
            }
        )
