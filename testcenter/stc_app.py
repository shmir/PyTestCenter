"""
This module implements classes and utility functions to manage STC application.

:author: yoram@ignissoft.com
"""
from __future__ import annotations

import logging
import time
from enum import Enum
from os import path
from typing import Optional, Union

from trafficgenerator.tgn_app import TgnApp
from trafficgenerator.tgn_utils import ApiType, TgnError

from testcenter import TYPE_2_OBJECT
from testcenter.api.stc_rest import StcRestWrapper
from testcenter.api.stc_tcl import StcTclWrapper
from testcenter.stc_object import StcObject
from testcenter.stc_project import StcProject


class StcSequencerOperation(Enum):
    start = "SequencerStart"
    stop = "SequencerStop"
    step = "SequencerStep"
    pause = "SequencerPause"
    wait = "waituntilcomplete"


def init_stc(
    api: ApiType,
    logger: logging.Logger,
    install_dir: Optional[str] = None,
    rest_server: Optional[str] = None,
    rest_port: Optional[int] = 80,
) -> StcApp:
    """Helper function to create STC object.

    This helper supports only new sessions. In order to connect to existing session on Lab server create
    StcRestWrapper and StcApp directly.

    :param api: tcl/python/rest
    :param logger: python logger object
    :param install_dir: STC installation directory
    :param rest_server: rest server address (either stcweb or lab server)
    :param rest_port: rest server port (either stcweb or lab server)
    """
    if api == ApiType.tcl:
        stc_api_wrapper = StcTclWrapper(logger, install_dir)
    elif api == ApiType.rest:
        stc_api_wrapper = StcRestWrapper(logger, rest_server, rest_port)
    else:
        raise TgnError(f"{api} API not supported - use Tcl or REST")
    return StcApp(logger, api_wrapper=stc_api_wrapper)


class StcApp(TgnApp):
    """TestCenter driver. Equivalent to TestCenter Application."""

    def __init__(self, logger: logging.Logger, api_wrapper: Union[StcRestWrapper, StcTclWrapper]) -> None:
        """Set all kinds of application level objects - logger, api, etc.

        :param logger: python logger (e.g. logging.getLogger('log'))
        :param api_wrapper: api wrapper object inheriting and implementing StcApi base class.
        """

        super().__init__(logger, api_wrapper)

        StcObject.logger = self.logger
        StcObject.str_2_class = TYPE_2_OBJECT

        self.system = StcObject(parent=None, objType="system", objRef="system1")
        self.system.api = self.api
        self.system.logger = self.logger
        self.lab_server = None
        self.project: StcProject = None
        self.hw = None

    def connect(self, lab_server=None) -> None:
        """Create object and (optionally) connect to lab server.

        :param lab_server: optional lab server address.
        """
        self.lab_server = lab_server
        if self.lab_server:
            self.api.perform("CSTestSessionConnect", Host=self.lab_server, CreateNewTestSession=True)

        # Every object creation/retrieval must come AFTER we connect to lab server (if needed).
        self.project = StcProject(parent=self.system)
        StcObject.project = self.project
        self.hw = self.system.get_child("PhysicalChassisManager")

    def disconnect(self, terminate=True) -> None:
        """Disconnect from lab server (if used) and reset configuration.

        :param terminate: True - terminate session, False - leave session on server.
        """
        self.reset_config()
        if type(self.api) == StcRestWrapper:
            self.api.disconnect(terminate)
        if self.lab_server:
            self.api.perform("CSTestSessionDisconnect", Terminate=terminate)

    def load_config(self, config_file_name: str) -> None:
        """Load configuration file from tcc or xml.

        Configuration file type is extracted from the file suffix - xml or tcc.

        :param config_file_name: full path to the configuration file.
        """

        if type(self.api) == StcRestWrapper:
            self.api.client.upload(config_file_name)
            config_file_name = path.basename(config_file_name)
        ext = path.splitext(config_file_name)[-1].lower()
        if ext == ".tcc":
            self.api.perform("LoadFromDatabase", DatabaseConnectionString=path.normpath(config_file_name))
        elif ext == ".xml":
            self.api.perform("LoadFromXml", FileName=path.normpath(config_file_name))
        else:
            raise ValueError(f"Configuration file type {ext} not supported.")
        self.project.objects = {}
        self.project.get_children("port")

    def reset_config(self):
        self.api.perform("ResetConfig", config="system1")

    def save_config(self, config_file_name: str, server_folder: Optional[str] = "c:\\temp") -> None:
        """Save configuration file as tcc or xml.

        Configuration file type is extracted from the file suffix - xml or tcc.

        :param config_file_name: full path to the configuration file.
        :param server_folder: folder on the server where the system will save the files before download.
        """
        if type(self.api) == StcRestWrapper:
            config_file_name_full_path = config_file_name
            config_file_name = server_folder + "\\" + path.basename(config_file_name)
        ext = path.splitext(config_file_name)[-1].lower()
        if ext == ".tcc":
            rc = self.api.perform("SaveToTcc", FileName=path.normpath(config_file_name))
        elif ext == ".xml":
            rc = self.api.perform("SaveAsXml", FileName=path.normpath(config_file_name))
        else:
            raise ValueError("Configuration file type {0} not supported.".format(ext))
        if type(self.api) == StcRestWrapper:
            self.api.client.download(rc["FileName"], config_file_name_full_path)

    def clear_results(self) -> None:
        self.project.clear_results()

    #
    # Online commands.
    # All commands assume that all ports are reserved and port objects exist under project.
    #

    def send_arp_ns(self) -> None:
        """Run ARP on all ports."""
        StcObject.send_arp_ns(*self.project.ports.values())

    def get_arp_cache(self):
        return StcObject.get_arp_cache(*self.project.get_objects_or_children_by_type("port"))

    #
    # Devices commands.
    #

    def start_devices(self) -> None:
        """Start all devices.

        It is the test responsibility to wait for devices to reach required state.
        """
        self._command_devices("DeviceStart")

    def stop_devices(self) -> None:
        """Stop all devices."""
        self._command_devices("DeviceStop")

    def _command_devices(self, command) -> None:
        self.project.command_devices(command, 4)
        self.project.test_command_rc("Status")
        time.sleep(4)

    #
    # Traffic commands.
    #

    def start_traffic(self, blocking: Optional[bool] = False) -> None:
        """Start traffic on all ports."""
        self.project.start_ports(blocking)

    def stop_traffic(self) -> None:
        """Stop traffic on all ports."""
        self.project.stop_ports()

    def wait_traffic(self) -> None:
        """Wait for traffic to end on all ports."""
        self.project.wait_traffic()

    #
    # Sequencer commands.
    #

    def sequencer_command(self, command: StcSequencerOperation) -> None:
        """Perform sequencer command.

        :param command: sequencer command.
        """
        if command != StcSequencerOperation.wait:
            self.project.command(command.value)
        else:
            self.project.wait()
