from setuptools import setup

setup(
        name='odk_servermanager',
        version='0.1',
        packages=['odk_servermanager'],
        include_package_data=True,
        license='GPLv3',
        author='Carlo De Pieri',
        description='ODKclan tool to manage its Arma 3 server instances.',
        install_requires=[
            'beautifulsoup4>=4.8.2',
            'Jinja2>=2.11.1',
            'python-box>=4.0.4'
            ],
        extras_require={
            'dev': [
                'pytest>=5.3.5',
                'pytest-mock>=2.0.0',
                'pytest-sugar>=0.9.2',
                ]
            }
        )
