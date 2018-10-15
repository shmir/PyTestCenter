"""
This module implements classes and utility functions to manage STC application.

:author: yoram@ignissoft.com
"""

from os import path
import time
from enum import Enum

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


class StcSequencerOperation(Enum):
    start = 'SequencerStart'
    stop = 'SequencerStop'
    step = 'SequencerStep'
    pause = 'SequencerPause'
    wait = 'waituntilcomplete'


def init_stc(api, logger, install_dir=None, rest_server=None, rest_port=80):
    """ Helper function to create STC object.

    This helper supports only new sessions. In order to connect to existing session on Lab server create
    StcRestWrapper and StcApp directly.

    :param api: tcl/python/rest
    :type api: trafficgenerator.tgn_utils.ApiType
    :param logger: python logger object
    :param install_dir: STC installation directory
    :param rest_server: rest server address (either stcweb or lab server)
    :param rest_port: rest server port (either stcweb or lab server)
    :return: STC object
    """

    if api == ApiType.tcl:
        stc_api_wrapper = StcTclWrapper(logger, install_dir)
    elif api == ApiType.python:
        stc_api_wrapper = StcPythonWrapper(logger, install_dir)
    elif api == ApiType.rest:
        stc_api_wrapper = StcRestWrapper(logger, rest_server, rest_port)
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

    def disconnect(self, terminate=True):
        """ Disconnect from lab server (if used) and reset configuration.

        :param terminate: True - terminate session, False - leave session on server.
        """

        self.reset_config()
        if type(self.api) == StcRestWrapper:
            self.api.disconnect(terminate)
        if self.lab_server:
            self.api.perform('CSTestSessionDisconnect', Terminate=terminate)

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
        self.project.get_children('port')

    def reset_config(self):
        self.api.perform('ResetConfig', config='system1')

    def save_config(self, config_file_name, server_folder='c:\\temp'):
        """ Save configuration file as tcc or xml.

        Configuration file type is extracted from the file suffix - xml or tcc.
        :param config_file_name: full path to the configuration file.
        :param server_temp_folder: folder on the server where the system will save the files before download.
        """

        if type(self.api) == StcRestWrapper:
            config_file_name_full_path = config_file_name
            config_file_name = server_folder + '\\' + path.basename(config_file_name)
        ext = path.splitext(config_file_name)[-1].lower()
        if ext == '.tcc':
            rc = self.api.perform('SaveToTcc', FileName=path.normpath(config_file_name))
        elif ext == '.xml':
            rc = self.api.perform('SaveAsXml', FileName=path.normpath(config_file_name))
        else:
            raise ValueError('Configuration file type {0} not supported.'.format(ext))
        if type(self.api) == StcRestWrapper:
            self.api.ls.download(rc['FileName'], config_file_name_full_path)

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

    #
    # Sequencer commands.
    #

    def sequencer_command(self, command):
        """ Perform sequencer command.

        :param command: sequencer command.
        :type command: testcenter.stc_app.StcSequencerOperation
        """
        if command != StcSequencerOperation.wait:
            self.project.command(command.value)
        else:
            self.project.wait()


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
                 'ipv4isisroutesconfig': StcIsisRouterRange,
                 'ipv6isisroutesconfig': StcIsisRouterRange,
                 'isisrouterconfig': StcIsisRouter,
                 'generator': StcGenerator,
                 'groupcollection': StcGroupCollection,
                 'ospfv2routerconfig': StcOspfv2Router,
                 'ospfv3asexternallsablock': StcOspfLsa,
                 'ospfv3interareaprefixlsablk': StcOspfLsa,
                 'ospfv3intraareaprefixlsablk': StcOspfLsa,
                 'ospfv3naaslsablock': StcOspfLsa,
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
