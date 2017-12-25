"""
This module implements classes and utility functions to manage STC application.

:author: yoram@ignissoft.com
"""

from os import path
import time
from random import randint

from trafficgenerator.tgn_utils import ApiType, TgnError
from trafficgenerator.tgn_app import TgnApp

from testcenter.api.stc_tcl import StcTclWrapper
from testcenter.api.stc_python import StcPythonWrapper
from testcenter.api.stc_rest import StcRestWrapper
from testcenter.stc_object import StcObject
from testcenter.stc_device import (StcDevice, StcServer, StcClient, StcBgpRouter, StcBgpRoute, StcPimRouter,
                                   StcPimv4Group, StcOspfv2Router, StcOspfLsa, StcIgmpHost, StcIgmpQuerier,
                                   StcIgmpGroup, StcOseSwitch, StcIsisRouter, StcBfdRouter, StcIsisRouterRange,
                                   StcBfdSession, StcRsvpRouter, StcRsvpTunnel)
from testcenter.stc_port import StcPort, StcGenerator, StcAnalyzer
from testcenter.stc_project import StcProject, StcIpv4Group, StcIpv6Group
from testcenter.stc_stream import StcStream, StcGroupCollection, StcTrafficGroup
from testcenter.stc_hw import StcHw, StcPhyChassis, StcPhyModule, StcPhyPortGroup, StcPhyPort


def init_stc(api, logger, install_dir=None, lab_server=None):
    """ Create STC object.

    :param api: tcl/python/rest
    :type api: trafficgenerator.tgn_utils.ApiType
    :param logger: python logger object
    :param install_dir: STC installation directory
    :param lab_server: lab server address
    :return: STC object
    """

    if api == ApiType.tcl:
        stc_api_wrapper = StcTclWrapper(logger, install_dir)
    elif api == ApiType.python:
        stc_api_wrapper = StcPythonWrapper(logger, install_dir)
    elif api == ApiType.rest:
        stc_api_wrapper = StcRestWrapper(logger, lab_server, session_name='session' + str(randint(0, 99)))
    else:
        raise TgnError('{} API not supported - use Tcl, python or REST'.format(api))
    return StcApp(logger, api_wrapper=stc_api_wrapper)


class StcApp(TgnApp):
    """ TestCenter driver. Equivalent to TestCenter Application. """

    def __init__(self, logger, api_wrapper):
        """ Set all kinds of application level objects - logger, api, etc.

        :param logger: python logger (e.g. logging.getLogger('log'))
        :param api_wrapper: api wrapper object inheriting and implementing StcApi base class.
        """

        super(self.__class__, self).__init__(logger, api_wrapper)

        StcObject.logger = self.logger
        StcObject.str_2_class = TYPE_2_OBJECT

        self.system = StcObject(objType='system', objRef='system1', parent=None)
        self.system.api = self.api
        self.system.logger = self.logger
        self.system.project = None

    def connect(self, lab_server=None):
        """ Create object and (optionally) connect to lab server.

        :param lab_server: optional lab server address.
        """

        self.lab_server = lab_server
        if self.lab_server:
            self.api.perform('CSTestSessionConnect', Host=self.lab_server, CreateNewTestSession=True)

        # Every object creation/retrieval must come AFTER we connect to lab server (if needed).
        self.hw = self.system.get_child('PhysicalChassisManager')
        self.project = StcProject(parent=self.system)
        self.project.project = self.project

    def disconnect(self):
        """ Disconnect from lab server (if used) and reset configuration. """

        self.reset_config()
        if type(self.api) == StcRestWrapper:
            self.api.disconnect()
        if self.lab_server:
            self.api.perform('CSTestSessionDisconnect', Terminate=True)

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
        self.project.objects = {}

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


TYPE_2_OBJECT = {'analyzer': StcAnalyzer,
                 'bfdipv4controlplaneindependentsession': StcBfdSession,
                 'bfdipv6controlplaneindependentsession': StcBfdSession,
                 'bfdrouterconfig': StcBfdRouter,
                 'bgprouterconfig': StcBgpRouter,
                 'bgpipv4routeconfig': StcBgpRoute,
                 'bgpipv6routeconfig': StcBgpRoute,
                 'dhcpv4serverconfig': StcServer,
                 'dhcpv4blockconfig': StcClient,
                 'emulateddevice': StcDevice,
                 'externallsablock': StcOspfLsa,
                 'igmphostconfig': StcIgmpHost,
                 'igmprouterconfig': StcIgmpQuerier,
                 'igmpgroupmembership': StcIgmpGroup,
                 'ipv4group': StcIpv4Group,
                 'ipv6group': StcIpv6Group,
                 'Ipv4IsisRoutesConfig': StcIsisRouterRange,
                 'Ipv6IsisRoutesConfig': StcIsisRouterRange,
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
                 'routerlsa': StcOspfLsa,
                 'rsvpegresstunnelparams': StcRsvpTunnel,
                 'rsvpingresstunnelparams': StcRsvpTunnel,
                 'rsvprouterconfig': StcRsvpRouter,
                 'streamblock': StcStream,
                 'summarylsablock': StcOspfLsa,
                 'trafficgroup': StcTrafficGroup,
                 }
