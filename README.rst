
TGN - Traffic Generator
STC - Spirent TestCenter.

This package implements Python OO API for STC.

The package works on top of multiple low level APIs:
1. StcTclWrapper - a Python wrapper (using Python Tk package) over STC native Tcl API (SpirentTestCenter) .
	Instead of using Tk (and SpirentTestCenter package) the calling application can provide its own connection to Tcl
	interpreter as long as the connection supports the 'eval' command and can perform STC Tcl API commands.
2. StcPythonWrapper - a Python wrapper over STC native Python API (StcPython.py)
3. StcRestWrapper - a Python wrapper over STC lab server REST API (using stcrestclient package).
4. Any StcCustomerApi as long as it supports the same API as all above APIs support (define ABC).

Logging:
- general messages + calls to underlining API + return values are logged to the logger provided by the application.
	API calls are logged at debug level 
- calls to underlining API are also logged to a separate file to create a 'script' that can be run 'as is'.
Currently supported only over serialized APIs - Tcl and custom.

Installation:
stable - pip instsll stcooapi
testing - pip install stcooapi -r --extra-index-url https://testpypi.python.org/pypi

Prerequisite:
TestCenter application installed for Tcl and Python API OR lab server installed for REST API.

Licensing:
This package uses STC Tcl API which is the default, non-licensed, API for STC.

Getting started:
Under testcenter.test.stc_samples you will find some basic samples.
See inside for more info.

Functionality
The current version supports the following test flow:
	Load configuration -> Get/Set attributes -> Start/Stop traffic -> Get statistics.
Supported operations:
	- Basic operations - get/set attributes, get/create children.
	- Connect - to chassis or lab server
	- Load configuration - load configuration (tcc or XML), reserve ports and analyze the configuration
	- Start/Stop - arp, ping, devices, ports, streams
	- Statistics - subscribe, read views, unsubscribe
	- Save configuration and results
	- Disconnect
The package also support Add/Remove objects so it supports the following test case:
	Build configuration -> Start/Stop traffic -> Get statistics.
But this is less documented at this version.

TestCenter and IxNetwork:
IxNetwork package and TestCenter extend the same base classes from TrafficGenerator.
In some future version we plan TrafficGenerator a complete abstract API so tests that work in the basic test flow will
be able to run over IxNetwork and TestCenter seamlessly.   

Contact:
Feel free to contact me with any question or feature request at yoram@ignissoft.com
