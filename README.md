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
$ git clone https://github.com/CarloDePieri/odk_servermanager.git odksm 
```
to download the tool. You can then keep it updated by running, in the `odksm` directory
```
$ git fetch
$ git pull
```

#### Install
Usage of a python virtual environment is strongly encouraged: install pipenv and prepare the venv by issuing these 
commands inside the ODKSM root directory:
```
$ pip install pipenv
$ python -m venv .venv
```
When the venv is ready, install ODKSM and its dependencies inside the venv with:
```
$ pipenv install --dev
```
You can verify that ODKSM is working as intended and all dependencies are met by running its test suite with:
```
$ pipenv run pytests tests/
```
All tests should pass.


## Create a server instance
To create your first instance you will need to fill in a copy of the config file `config.ini` that can be found
in the root directory of this tool.

The default `config.ini` contains detailed descriptions of every possible option that can be passed to the tool. 

Options from the `config` and `bat` sections will be used to fill in templates for the serverConfig.cfg (the file 
that will be passed with the -config flag to the server) and run_server.bat (the bat that will be used to launch 
the instance).

Options from the `ODKSM` section will be used directly in the tool to set paths, mods and keys, amongst other things. 
Particularly you can specify user mods via a list in the config or passing the path of a mods preset file shared by the 
Arma 3 Launcher. 

Once your config is in order, you may simply drag&drop your config file, e.g. `your_config.ini`, on the `ODKSM.bat` 
to launch the tool.

Alternatively, in the shell:
```
$ ODKSM.bat your_config.ini
```

To launch the instance then simply run:
```
$ run_server.bat
```

## Update a server instance
You can update a server instance if you want to change mission, mods or just a field somewhere. Simply update your 
`config.ini` and relaunch `ODKSM.bat` via drag&drop or shell.

This will re-link / re-copy mods, reset keys and re-compile config files.

Keep in mind that when updating mods in the Arma 3 `!Workshop` folder the keys files will probably change. Sadly there's
 no way to magically link them in the instance, since the name of the file change. This means that after updating the mods
 you probably will need to update your server instance with ODKSM to re-link keys file.
 
 
## How does it work?
TODO
