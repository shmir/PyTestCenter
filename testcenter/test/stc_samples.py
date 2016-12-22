"""
Stand alone samples for STC package functionality.

Setup:
Two STC ports connected back to back.

@author yoram@ignissoft.com
"""

import sys
from os import path
import unittest
import logging
import time

from trafficgenerator.tgn_utils import is_false

from testcenter.api.stc_tcl import StcTclWrapper
from testcenter.api.stc_python import StcPythonWrapper
from testcenter.api.stc_rest import StcRestWrapper
from testcenter.stc_app import StcApp
from ixnetwork.ixn_statistics_view import IxnPortStatistics, IxnTrafficItemStatistics


# API type = tcl, python or rest. Default is tcl with DEBUG log messages (see bellow) because it gives best visibility.
api = 'tcl'
install_dir = 'C:/Program Files (x86)/Spirent Communications/Spirent TestCenter 4.66'

stc_config_file = path.join(path.dirname(__file__), 'configs/test_config.tcc')

port1_location = '10.192.18.200/2/5'
port2_location = '10.192.18.200/2/8'


class IxnTestBase(unittest.TestCase):

    def setUp(self):
        super(IxnTestBase, self).setUp()
        logger = logging.getLogger('log')
        logger.setLevel('DEBUG')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        if api == 'tcl':
            api_wrapper = StcTclWrapper(logger, install_dir)
        elif api == 'python':
            api_wrapper = StcPythonWrapper(logger, install_dir)
        else:
            api_wrapper = StcRestWrapper(logger, install_dir)
        self.stc = StcApp(logger, api_wrapper=api_wrapper)
        self.stc.connect()

    def tearDown(self):
        super(IxnTestBase, self).tearDown()

    def load_config(self):
        self.stc.load_config(stc_config_file)

    def objects_access(self):
        self.load_config()

        # You can read all objects by calling the general method get_children
        ports = self.stc.project.get_children('port')
        assert(len(ports) == 2)
        # After the objects have been read from IXN you can retrieve them from memory (much faster)
        ports = self.stc.project.get_objects_by_type('port')
        assert(len(ports) == 2)
        # If you are not sure if objects have been read from IXN yet (best method for static configurations)
        ports = self.stc.project.get_objects_or_children_by_type('port')
        assert(len(ports) == 2)

        # Now we can iterate and print all objects:
        print 'Name\tObject Reference\tPython Object'
        for port in ports:
            print '{}\t{}\t{}'.format(port.obj_name(), port.obj_ref(), port)

        # But... frequently used objects (like ports...) can be accessed specifically:
        ports = self.stc.project.get_ports()
        assert(len(ports) == 2)

        # Now we can iterate and print all objects:
        print 'Name\tObject Reference\tPython Object'
        for name, obj in ports.items():
            print '{}\t{}\t{}'.format(name, obj.obj_ref(), obj)

    def get_set_attribute(self):
        self.load_config()
        device = self.stc.project.get_ports()['Port 1'].get_devices()['Device 1']

        # Get all attributes
        print device.get_attributes()

        # Get group of attributes
        print device.get_attributes('RouterId', 'RouterIdStep')

        # Get specific attribute
        print 'RouterId: ' + device.get_attribute('RouterId')

        # Special cases - name and active
        print 'name: ' + device.get_name()
        print 'enabled: ' + str(device.get_active())

        # Set attribute
        device.set_attributes(RouterId='1.2.3.4')
        assert(device.get_attribute('RouterId') == '1.2.3.4')

        # And again, special case for active
        device.set_active(False)
        assert(is_false(device.get_active()))

    def reserve_ports(self):
        self.load_config()
        self.ports = self.ixn.root.get_children('vport')
        self.ixn.root.get_object_by_name('Port 1').reserve(port1_location)
        self.ixn.root.get_object_by_name('Port 2').reserve(port2_location)

    def protocols(self):
        self.reserve_ports()
        self.ixn.send_arp_ns()
        self.ixn.protocols_start()

    def traffic(self):
        self.reserve_ports()
        self.ixn.traffic_apply()
        self.ixn.l23_traffic_start()
        time.sleep(8)
        self.ixn.l23_traffic_stop()
        port_stats = IxnPortStatistics()
        port_stats.read_stats()
        ti_stats = IxnTrafficItemStatistics()
        ti_stats.read_stats()
        print port_stats.get_object_stats('Port 1')
        print port_stats.get_counters('Frames Tx.')
        assert(ti_stats.get_counter('Traffic Item 1', 'Rx Frames') == 1600)
