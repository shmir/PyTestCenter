
## Python OO API for Spirent TestCenter (STC).

### Functionality
The current version supports the following test flow:

- Load configuration -> Get/Set attributes -> Start/Stop traffic -> Get statistics.
   
Supported operations:

- Basic operations - get/set attributes, get/create children.
- Connect - to chassis or lab server
- Load configuration - load configuration (tcc or XML), reserve ports and analyze the configuration
- Start/Stop - arp, ping, devices, ports, streams
- Statistics - subscribe, read views, unsubscribe
- Save configuration and results
- Disconnect

The package also support Add/Remove objects so it supports the following test case:

- Build configuration -> Start/Stop traffic -> Get statistics.

But this is less documented at this version.

### Low level APIs

- StcTclWrapper - a Python wrapper (using Python Tk package) over STC native Tcl API (SpirentTestCenter) .
- StcPythonWrapper - a Python wrapper over STC native Python API (StcPython.py)
- StcRestWrapper - a Python wrapper over STC lab server REST API (using stcrestclient package).

### Installation
pip instsll pytestcenter

**Prerequisite**<br>
TestCenter application installed for Tcl and Python APIs.<br>
Lab/Rese server for REST API.

### Getting started
Under testcenter.test.stc_samples you will find some basic samples.
See inside for more info.

### Documentation
http://pytestcenter.readthedocs.io/en/latest/

### Contact
Feel free to contact me with any question or feature request at yoram@ignissoft.com
