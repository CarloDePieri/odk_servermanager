from setuptools import setup

setup(
        name='odk_servermanager',
        version='1.0.0',
        packages=['odk_servermanager'],
        include_package_data=True,
        license='GPLv3',
        author='Carlo De Pieri',
        description='ODK Clan tool to manage its Arma 3 server instances.',
        install_requires=[
            'beautifulsoup4>=4.8.2',
            'Jinja2>=2.11.1',
            'python-box>=4.0.4',
            "reusables>=0.9.5"
            ],
        extras_require={
            'dev': [
                'pytest>=5.3.5',
                'pytest-mock>=2.0.0',
                'pytest-sugar>=0.9.2',
                'pytest-cov>=2.8.1',
                'coveralls>=1.11.1'
                ]
            }
        )
