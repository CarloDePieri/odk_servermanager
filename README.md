# ODK Server Manager
[![CI](https://github.com/CarloDePieri/odk_servermanager/actions/workflows/ci.yml/badge.svg)](https://github.com/CarloDePieri/odk_servermanager/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/CarloDePieri/odk_servermanager/badge.svg?branch=master)](https://coveralls.io/github/CarloDePieri/odk_servermanager?branch=master)
![Supported Operating System](https://img.shields.io/badge/os-Windows-blue)
![Maintenance](https://img.shields.io/maintenance/yes/2024)
[![Documentation Status](https://readthedocs.org/projects/odksm/badge/?version=latest)](https://odksm.readthedocs.io/en/latest/?badge=latest)

[<img src="https://www.odkclan.it/img/ODK-logo.jpg" height="100">](https://www.odkclan.it/)

ODKSM is an open source python tool to quickly and easily create more than one Arma 3 server instance and manage their
settings, mods and keys. It does so by intelligently using symlinks, which keeps server instances' folders small, easy
to update and archive.

It mainly caters to dedicated server maintainers, but could surely come in handy for mission makers.

Main features:

* Having separated server instances and mixing symlink with real configuration file result in a clean and organized Arma 3 main folder
* **ONE** easy to understand and thoroughly documented configuration file to manage the whole instance
* Flexible .bat scripts to call the tool that can easily adapt to different folders structures
* Simply running the tool is enough to keep mods, keys and Arma configuration files updated
* Quickstart tool to automate initial creation of multiple instances
* Modular architecture that allows to quickly implement mod specific behaviour
* Configuration file templates support

Check out our detailed documentation on readthedocs ([english](https://odksm.readthedocs.io/en/latest/) or [italian](https://odksm.readthedocs.io/it/latest/)).