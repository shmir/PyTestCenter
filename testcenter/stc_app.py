"""
This module implements classes and utility functions to manage STC application.

:author: yoram@ignissoft.com
"""

from os import path
import sys
import time
import logging

from trafficgenerator.trafficgenerator import TrafficGenerator

from testcenter.api.stc_rest import StcRestWrapper
from stc_object import StcObject
from stc_device import (StcDevice, StcServer, StcClient, StcBgpRouter, StcBgpRoute, StcPimRouter, StcPimv4Group,
                        StcOspfv2Router, StcRouterLsa, StcIgmpHost, StcIgmpQuerier, StcIgmpGroup, StcOseSwitch,
                        StcIsisRouter)
from stc_port import StcPort, StcGenerator, StcAnalyzer
from stc_project import StcProject, StcIpv4Group, StcIpv6Group
from stc_stream import StcStream, StcGroupCollection, StcTrafficGroup
from stc_hw import StcHw, StcPhyChassis, StcPhyModule, StcPhyPortGroup, StcPhyPort

TYPE_2_OBJECT = {'analyzer': StcAnalyzer,
                 'bgprouterconfig': StcBgpRouter,
                 'bgpipv4routeconfig': StcBgpRoute,
                 'dhcpv4serverconfig': StcServer,
                 'dhcpv4blockconfig': StcClient,
                 'emulateddevice': StcDevice,
                 'externallsablock': StcRouterLsa,
                 'igmphostconfig': StcIgmpHost,
                 'igmprouterconfig': StcIgmpQuerier,
                 'igmpgroupmembership': StcIgmpGroup,
                 'ipv4group': StcIpv4Group,
                 'ipv6group': StcIpv6Group,
                 'isisrouterconfig': StcIsisRouter,
                 'generator': StcGenerator,
                 'groupcollection': StcGroupCollection,
                 'ospfv2routerconfig': StcOspfv2Router,
                 'oseswitchconfig': StcOseSwitch,
                 'pimrouterconfig': StcPimRouter,
                 'pimv4groupblk': StcPimv4Group,
                 'port': StcPort,
                 'physicalchassis': StcPhyChassis,
                 'physicalchassismanager': StcHw,
                 'physicalport': StcPhyPort,
                 'physicalportgroup': StcPhyPortGroup,
                 'physicaltestmodule': StcPhyModule,
                 'routerlsa': StcRouterLsa,
                 'streamblock': StcStream,
                 'summarylsablock': StcRouterLsa,
                 'trafficgroup': StcTrafficGroup,
                 }


class StcApp(TrafficGenerator):
    """ TestCenter driver. Equivalent to TestCenter Application. """

    lab_server = None

    system = None
    project = None

    def __init__(self, logger, api_wrapper):
        """ Set all kinds of application level objects - logger, api, etc.

        :param logger: python logger (e.g. logging.getLogger('log'))
        :param api_wrapper: api wrapper object inheriting and implementing StcApi base class.
        """

        super(self.__class__, self).__init__()
        self.logger = logger
        self.api = api_wrapper

        StcObject.logger = self.logger
        StcObject.api = self.api
        StcObject.str_2_class = TYPE_2_OBJECT

        self.system = StcObject(objType='system', objRef='system1')
        self.hw = self.system.get_child('PhysicalChassisManager')

    def connect(self, lab_server=None):
        """ Create object and (optionally) connect to lab server.

        :param lab_server: optional lab server address.
        """

        self.project = StcProject(parent=self.system)
        StcObject.project = self.project
        self.lab_server = lab_server
        if self.lab_server:
            self.api.perform('CSTestSessionConnect', Host=self.lab_server, CreateNewTestSession=True)

    def disconnect(self):
        """ Disconnect from lab server (if used) and reset configuration. """

        if self.lab_server:
            self.api.perform('CSTestSessionDisconnect', Terminate=True)
        self.reset_config()

    def load_config(self, config_file_name):
        """ Load configuration file from tcc or xml.

        Configuration file type is extracted from the file suffix - xml or tcc.

        :param config_file_name: full path to the configuration file.
        """

        if type(self.api) == StcRestWrapper:
            self.api.ls.upload(config_file_name)
            config_file_name = path.basename(config_file_name)
        ext = path.splitext(config_file_name)[-1].lower()
        if ext == '.tcc':
            self.api.perform('LoadFromDatabase', DatabaseConnectionString=path.normpath(config_file_name))
        elif ext == '.xml':
            self.api.perform('LoadFromXml', FileName=path.normpath(config_file_name))
        else:
            raise ValueError('Configuration file type {} not supported.'.format(ext))

    def reset_config(self):
        self.api.perform('ResetConfig', config='system1')

    def save_config(self, config_file_name):
        """ Save configuration file as tcc or xml.

        Configuration file type is extracted from the file suffix - xml or tcc.
        :param config_file_name: full path to the configuration file.
        """

        ext = path.splitext(config_file_name)[-1].lower()
        if ext == '.tcc':
            self.api.perform('SaveToTcc', FileName=path.normpath(config_file_name))
        elif ext == '.xml':
            self.api.perform('SaveAsXml', FileName=path.normpath(config_file_name))
        else:
            raise ValueError('Configuration file type {0} not supported.'.format(ext))

    def clear_results(self):
        self.project.clear_results()

    #
    # Online commands.
    # All commands assume that all ports are reserved and port objects exist under project.
    #

    def send_arp_ns(self):
        StcObject.send_arp_ns(*self.project.get_objects_or_children_by_type('port'))

    def get_arp_cache(self):
        return StcObject.get_arp_cache(*self.project.get_objects_or_children_by_type('port'))

    #
    # Devices commands.
    #

    def start_devices(self):
        """ Start all devices.

        It is the test responsibility to wait for devices to reach required state.
        """
        self._command_devices('DeviceStart')

    def stop_devices(self):
        self._command_devices('DeviceStop')

    def _command_devices(self, command):
        self.project.command_devices(command, 4)
        self.project.test_command_rc('Status')
        time.sleep(4)

    #
    # Traffic commands.
    #

    def start_traffic(self, blocking=False):
        self.project.start_ports(blocking)

    def stop_traffic(self):
        self.project.stop_ports()

    def wait_traffic(self):
        self.project.wait_traffic()


def testcenter(args):
    """ Stand alone STC application.

    Serves as code snippet and environment testing.
    """

    # TODO: replace with ini file.
    install_dir = 'C:/Program Files (x86)/Spirent Communications/Spirent TestCenter 4.60'
    log_level = 'INFO'
    log_file_name = 'test/logs/testcenter.txt'

    logger = logging.getLogger('log')
    logger.setLevel(log_level)
    logger.addHandler(logging.FileHandler(log_file_name))
    logger.addHandler(logging.StreamHandler(sys.stdout))

    stc = StcApp(logger, install_dir)
    stc.system.get_child('automationoptions').set_attributes(LogLevel=log_level)
    stc.connect()

if __name__ == "__main__":
    sys.exit(testcenter((sys.argv[1:])))
