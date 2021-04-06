"""
Stand alone samples for STC package functionality.

Setup:
Two STC ports connected back to back.
"""
import json
import logging
import sys
import time
from pathlib import Path

from trafficgenerator.tgn_utils import is_false, ApiType

from testcenter.stc_app import init_stc
from testcenter.stc_statistics_view import StcStats


logger = logging.getLogger('log')
logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler(sys.stdout))

api = ApiType.rest
install_dir = 'C:/Program Files/Spirent Communications/Spirent TestCenter 5.11'
lab_server = None
rest_server = '10.100.102.25'
rest_port = 8888

stc_config_file = Path(__file__).parent.joinpath('test_config.xml')

port1_location = '192.168.65.24/1/1'
port2_location = '192.168.65.24/1/2'


def access_object():

    # You can read all objects by calling the general method get_children
    stc.project.get_children('port')

    # After the objects have been read from STC you can retrieve them from memory (much faster)
    stc.project.get_objects_by_type('port')

    # If you are not sure if objects have been read from IXN yet (best method for static configurations)
    stc.project.get_objects_or_children_by_type('port')

    # But... frequently used objects (like ports...) can be accessed specifically:
    ports = stc.project.ports
    assert(len(ports) == 2)

    # Now we can iterate and print all objects:
    print('Name\tObject Reference\tPython Object')
    for port in ports.values():
        print(f'{port.name}\t{port.ref}\t{port}')


def get_set_attribute():

    device = stc.project.ports['Port 1'].devices['Device 1']

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


def reserve_ports():

    # To reserve a port, you need to map it to a location.
    stc.project.ports['Port 1'].reserve(port1_location)
    stc.project.ports['Port 2'].reserve(port2_location)


def manage_devices():

    stc.send_arp_ns()
    print(stc.get_arp_cache())
    stc.start_devices()
    time.sleep(8)
    stc.stop_devices()


def manage_traffic():

    stc.start_traffic()
    time.sleep(8)
    stc.stop_traffic()
    port_stats = StcStats('generatorportresults')
    port_stats.read_stats()

    # You can get a table of all counters, similar to the GUI.
    print(port_stats.get_all_stats().dumps(indent=2))

    # Or a table of all counters of a specific object.
    print(json.dumps(port_stats.get_object_stats('Port 1'), indent=2))

    # Or a list of all values of a specific counters for all objects.
    print(port_stats.get_column_stats('TotalFrameCount'))

    # Or a single value of of a single counter os a single object.
    print(port_stats.get_stat('Port 1', 'TotalFrameCount'))


def get_inventory():

    chassis = stc.hw.get_chassis(port1_location.split('/')[0])
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


if __name__ == '__main__':
    stc = init_stc(api, logger, install_dir=install_dir, rest_server=rest_server, rest_port=rest_port)
    stc.connect(lab_server)
    stc.load_config(stc_config_file)
    stc.api.apply()
    # access_object()
    # get_set_attribute()
    # get_inventory()
    reserve_ports()
    # manage_devices()
    manage_traffic()
    stc.disconnect(terminate=False)
