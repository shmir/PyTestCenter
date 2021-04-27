[![Python 3.7|3.8|3.9](https://img.shields.io/badge/python-3.7%7C3.8%7C.3.9-blue.svg)](https://www.python.org/downloads/release/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Build status](https://github.com/shmir/PyTestCenter/actions/workflows/python-package.yml/badge.svg?branch=dev)

# Python OO API for Spirent TestCenter (STC).

## Functionality
The current version supports the following test flow:

- Load configuration -> Get/Set attributes -> Start/Stop traffic -> Get statistics.
- Build configuration -> Start/Stop traffic -> Get statistics.

Supported operations:

- Basic operations - get/set attributes, get/create children
- Connect - to chassis or lab server
- Load configuration - load configuration (tcc or XML), reserve ports and analyze the configuration
- Start/Stop - arp, ping, devices, ports, streams
- Statistics - subscribe, read views, unsubscribe
- Save configuration and results
- Disconnect

## Low level APIs

- StcRestWrapper - a Python wrapper over STC lab server REST API (using stcrestclient package).
- StcTclWrapper - a Python wrapper (using Python Tk package) over STC native Tcl API (SpirentTestCenter) .

## Installation

pip install pytestcenter

**Prerequisite**

- Lab/Rest server for REST API.
- TestCenter application installed for Tcl

## Getting started
Under testcenter.test.stc_samples you will find some basic samples.
See inside for more info.

## Documentation
http://pytestcenter.readthedocs.io/en/latest/

## Contact
Feel free to contact me with any question or feature request at yoram@ignissoft.com

## Change Log
[ChangeLog.md](ChangeLog.md)
