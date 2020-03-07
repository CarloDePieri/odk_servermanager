# ODK Server Manager
[![Build Status](https://travis-ci.com/CarloDePieri/odk_servermanager.svg?branch=master)](https://travis-ci.com/CarloDePieri/odk_servermanager)
[![Coverage Status](https://coveralls.io/repos/github/CarloDePieri/odk_servermanager/badge.svg?branch=master)](https://coveralls.io/github/CarloDePieri/odk_servermanager?branch=master)

[<img src="https://www.odkclan.it/immagini/loghi/logo_home.png" height="100">](https://www.odkclan.it/)

ODKSM is a tool to quickly and easily create more than one Arma 3 server instance, its settings, mods and keys. It does 
so by intelligently using symlinks, which keeps the server instance's folder small and manageable.

## Installation

#### Prerequisites
The tool is currently compatible with Windows only (linux support is on its way).

You will need Python 3.8 installed on your machine. You can install it via 
[choco](https://chocolatey.org/packages/python/3.8.2) or via the [official package](https://www.python.org/ftp/python/3.8.2/python-3.8.2.exe).

#### Download
The quickest way to get this tool is to download the latest release from github.

If you want to be able to keep the tool updated, however, you may find it more convenient to use [git](https://git-scm.com/download/win).
Once installed, you may run 
```
$ git clone https://github.com/CarloDePieri/odk_servermanager.git 
```
to download the tool. You can then keep it updated by running, in the odk_servermanager directory
```
$ git fetch
$ git pull
```

#### Install with pipenv
Usage of a python virtual environment is strongly encouraged: install pipenv and prepare the venv by issuing these 
commands inside the odk_servermanager directory:
```
$ pip install pipenv
$ python -m venv .venv
```
When the venv is ready, install ODKSM and its dependencies inside the venv with:
```
$ pip install --dev
```
You can verify that ODKSM is working as intended and all dependencies are met by running its test suite with:
```
$ pipenv run pytests tests/
```
All tests should pass.
