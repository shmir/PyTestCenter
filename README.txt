# TestCenter

+++ WORK IN PROGRESS - fully functional, testing, documentation and packaging under construction. +++

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
