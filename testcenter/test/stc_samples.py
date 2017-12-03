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
from testcenter.stc_statistics_view import StcStats


# API type = tcl, python or rest. Default is tcl with DEBUG log messages (see bellow) because it gives best visibility.
api = 'tcl'
install_dir = 'C:/Program Files (x86)/Spirent Communications/Spirent TestCenter 4.80'
lab_server = ''

stc_config_file = path.join(path.dirname(__file__), 'configs/test_config.tcc')

port1_location = '10.210.3.10/2/1'
port2_location = '10.210.3.10/2/2'


class StcSamples(unittest.TestCase):

    def setUp(self):
        super(StcSamples, self).setUp()
        logger = logging.getLogger('log')
        logger.setLevel('DEBUG')
        logger.addHandler(logging.StreamHandler(sys.stdout))
        if api == 'tcl':
            api_wrapper = StcTclWrapper(logger, install_dir)
        elif api == 'python':
            api_wrapper = StcPythonWrapper(logger, install_dir)
        else:
            api_wrapper = StcRestWrapper(logger, lab_server)
        self.stc = StcApp(logger, api_wrapper=api_wrapper)
        self.stc.connect(lab_server)

    def tearDown(self):
        self.stc.disconnect()
#         super(StcSamples, self).tearDown()

    def load_config(self):
        self.stc.load_config(stc_config_file)
        self.stc.api.apply()

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
        print('Name\tObject Reference\tPython Object')
        for port in ports:
            print('{}\t{}\t{}'.format(port.obj_name(), port.obj_ref(), port))

        # But... frequently used objects (like ports...) can be accessed specifically:
        ports = self.stc.project.get_ports()
        assert(len(ports) == 2)

        # Now we can iterate and print all objects:
        print('Name\tObject Reference\tPython Object')
        for name, obj in ports.items():
            print('{}\t{}\t{}'.format(name, obj.obj_ref(), obj))

    def get_set_attribute(self):
        self.load_config()
        device = self.stc.project.get_ports()['Port 1'].get_devices()['Device 1']

        # Get all attributes
        print(device.get_attributes())

        # Get group of attributes
        print(device.get_attributes('RouterId', 'RouterIdStep'))

        # Get specific attribute
        print('RouterId: ' + device.get_attribute('RouterId'))

        # Special cases - name and active
        print('name: ' + device.get_name())
        print('enabled: ' + str(device.get_active()))

        # Set attribute
        device.set_attributes(RouterId='1.2.3.4')
        assert(device.get_attribute('RouterId') == '1.2.3.4')

        # And again, special case for active
        device.set_active(False)
        assert(is_false(device.get_active()))

    def reserve_ports(self):
        self.load_config()
        self.ports = self.stc.project.get_ports()
        self.ports['Port 1'].reserve(port1_location)
        self.ports['Port 2'].reserve(port2_location)

    def devices(self):
        self.reserve_ports()
        self.stc.send_arp_ns()
        print(self.stc.get_arp_cache())
        self.stc.start_devices()
        time.sleep(8)
        self.stc.stop_devices()

    def traffic(self):
        self.reserve_ports()
        self.stc.start_traffic()
        time.sleep(8)
        self.stc.stop_traffic()
        port_stats = StcStats(self.stc.project, 'generatorportresults')
        port_stats.read_stats()
        print(port_stats.get_object_stats('Port 1'))
        print(port_stats.get_stats('TotalFrameCount'))
        print(port_stats.get_stat('Port 1', 'TotalFrameCount'))

    def inventory(self):

        chassis = self.stc.hw.get_chassis(port1_location.split('/')[0])
        chassis.get_inventory()

        print('Full Inventory')
        print('=' * len('Full Inventory'))
        print(chassis.name)
        print(chassis.attributes)
        for module_name, module in chassis.modules.items():
            print('\t' + module_name)
            print('\t' + str(module.attributes))
            for pg_name, pg in module.pgs.items():
                print('\t\t' + pg_name)
                print('\t\t' + str(pg.attributes))
                for port_name, port in pg.ports.items():
                    print('\t\t\t' + port_name)
                    print('\t\t\t' + str(port.attributes))
        for ps_name in chassis.pss:
            print('\t' + ps_name)

        print('\nThin Inventory')
        print('=' * len('Thin Inventory'))
        for module_name, module in chassis.get_thin_inventory().items():
            print(module_name)
            for port_name in module.ports:
                print(port_name)
