"""
This module implements classes and utility functions to manage STC project.

Any command that can act on list of objects (ports, devices, emulations etc.) should be implemented
by StcProject.
"""

import time
from collections import OrderedDict

from trafficgenerator.tgn_tcl import build_obj_ref_list

from testcenter.stc_object import StcObject
from testcenter.stc_port import StcPort

command_2_config_object = {'Dhcpv4Bind': 'dhcpv4blockconfig',
                           'Dhcpv4Release': 'dhcpv4blockconfig',
                           'Dhcpv4StartServer': 'dhcpv4serverconfig',
                           'Dhcpv4StopServer': 'dhcpv4serverconfig',
                           'Dhcpv6StartServer': 'dhcpv6serverconfig',
                           'Dhcpv6Release': 'dhcpv6blockconfig',
                           'Dhcpv6Bind': 'dhcpv6blockconfig',
                           'Dhcpv6StopServer': 'dhcpv6serverconfig',
                           }


# StcProject serves as manager for its children - ports and devices.
class StcProject(StcObject):
    """ Represents STC project object. """

    wait_for_ports = 4

    def __init__(self, **data):
        super(StcProject, self).__init__(objType='project', **data)
        self.ports = OrderedDict()

    def reserve_ports(self, ports_locations, force=False, clear=True):
        """ Reserve ports and reset factory defaults.

        :param ports_locations: list of ports ports_locations <ip, card, port> to reserve
        :param force: True - take forcefully, False - fail if port is reserved by other user
        :param clear: True - clear port configuration and statistics, False - leave port as is
        :return: ports dictionary (port uri, port object)
        """
        p_list = []
        for i, port_location in enumerate(ports_locations):
            port = self.add_port(i,port_location)
            p_list.append(port.ref)
            #if clear:
                #port.clear()
            self.api.perform('AttachPorts', PortList=port.ref, AutoConnect=True, RevokeOwner=force)
        #TODO debug reserve p_list
        self.api.apply()
        return self.ports

    def add_port(self, p_name, location=None):
        self.ports[p_name] = StcPort(parent=self, name=p_name)
        if location:
            self.ports[p_name].location = location
        return self.ports[p_name]

    def get_ports(self):
        """
        :return: dictionary {name: object} of all port.
        """

        return {o.obj_name(): o for o in self.get_objects_or_children_by_type('Port')}
    #
    # Port command.
    #

    def start_ports(self, blocking=False, *ports):
        """ Start traffic on ports.

        :param blocking: True - wait for traffic end, False - return after traffic start.
        :param ports: list of ports to start traffic on, if empty start on all ports.
        """

        self._command_generator('GeneratorStart', *ports)
        self.test_command_rc('Status')
        if blocking:
            self.wait_traffic(*ports)

    def stop_ports(self, *ports):
        """ Stop traffic on ports.

        :param ports: list of ports to stop traffic on, if empty start on all ports.
        """

        self._command_generator('GeneratorStop', *ports)

    def wait_traffic(self, *ports):
        """ Wait for traffic end on ports.

        :param ports: list of ports to wait for, if empty wait for all ports.
        """

        for port in self._get_ports(*ports):
            while port.is_running():
                time.sleep(1)

    def clear_results(self, *ports):
        """ Clear emulations and traffic results on ports.

        :param ports: list of ports to clear results on, if empty clear results for all ports.
        """

        self.api.perform('ResultsClearAllCommand', PortList=build_obj_ref_list(self._get_ports(*ports)))
        self.api.perform('ResultsClearAllProtocolCommand')
        time.sleep(1)

    #
    # Device command.
    #

    def get_devices(self, *ports):
        """
        :param ports: list of ports to get devices for, if empty get for all ports.
        :return: list of requested devices.
        """

        devices = []
        for port in self._get_ports(*ports):
            devices.extend(port.get_children('emulateddevice'))
        return devices

    def get_emulations(self, emulation, *ports):
        """
        :param emulation: requested emulation class.
        :param ports: list of ports to get emulations for, if empty get for all ports.
        :return: list of requested emulations.
        """

        emulations = []
        for device in self.get_devices(*ports):
            emulations.extend(device.get_objects_or_children_by_type(emulation))
        return emulations

    def command_devices(self, command, wait_after=4, *devices, **arguments):
        """ Perform device command on list of devices.

        :param command: requested command.
        :param wait_after: time to wait after command execution in seconds.
        :param devices: list of devices to act on. If list is empty - perform on all devices.
        :param arguments: additional optional arguments per requested command.
        """

        arguments['DeviceList'] = build_obj_ref_list(self._get_devices(*devices))
        self.command(command, wait_after, **arguments)

    def command_device_emulations(self, command, wait_after=4, *devices, **arguments):
        """ Perform emulation command on list of devices.

        Use this method for all emulation specific commands.
        For emulation start/stop use start_emulation and stop_emulation accordingly.

        :param command: requested command.
        :param wait_after: time to wait after command execution in seconds.
        :param devices: list of devices to act on. If list is empty - perform on all devices.
        :param arguments: additional optional arguments per requested command.
        """

        emulation_child = command_2_config_object[command]
        emulations = []
        for device in self._get_devices(*devices):
            emulation = device.get_child(emulation_child)
            if emulation:
                emulations.append(emulation)
        if emulations:
            self.command_emulations(command, wait_after, *emulations, **arguments)

    def command_emulations(self, command, wait_after=4, *emulations, **arguments):
        """ Perform emulation command on list of emulations.

        Use this method for all emulation specific commands.
        For emulation start/stop use start_emulation and stop_emulation accordingly.

        :param command: requested command.
        :param wait_after: time to wait after command execution in seconds.
        :param emulations: list of emulations to act on.
        :param arguments: additional optional arguments per requested command.
        """

        arguments[emulations[0].objects_list] = build_obj_ref_list(emulations)
        self._command_emulations(command, wait_after, **arguments)

    def start_emulations(self, emulations, wait_after=4):
        """ Start emulations.

        :param emulations: list of emulations to act on.
        :param wait_after: time to wait after command execution in seconds.
        """

        self._command_emulations('ProtocolStart', wait_after, ProtocolList=build_obj_ref_list(emulations))

    def stop_emulations(self, emulations, wait_after=4):
        """ Start emulations.

        :param emulations: list of emulations to act on.
        :param wait_after: time to wait after command execution in seconds.
        """

        self._command_emulations('ProtocolStop', wait_after, ProtocolList=build_obj_ref_list(emulations))

    def get_stream_blocks(self):
        """
        :return: all stream blocks in the configuration.
        """

        streamblocks = []
        for port in self.project.get_objects_by_type('port'):
            streamblocks.extend(port.get_children('streamblock'))
        return streamblocks

    #
    # private methods.
    #

    def _get_ports(self, *ports):
        return ports if ports else self.get_objects_or_children_by_type('port')

    def _get_devices(self, *devices):
        return devices if devices else self.get_devices()

    def _command_emulations(self, command, wait_after, **arguments):
        self.command(command, **arguments)
        time.sleep(wait_after)

    def _command_generator(self, command, *ports):
        generators = []
        for port in self._get_ports(*ports):
            generators.extend(port.get_objects_by_type('generator'))
        self.api.perform(command, GeneratorList=build_obj_ref_list(generators))
        time.sleep(self.wait_for_ports)


class StcIpGroup(StcObject):
    """ Base class for STC IP groups. """

    def __init__(self, **data):
        super(StcIpGroup, self).__init__(**data)
        if 'joinedGroup' in data:
            self.set_sources(JoinedGroup=data['joinedGroup'].obj_ref())


class StcIpv4Group(StcIpGroup):
    """ Represents STC IPv4 group. """

    def __init__(self, **data):
        data['objType'] = 'Ipv4Group'
        super(self.__class__, self).__init__(**data)
        self.network_block = self.get_child('Ipv4NetworkBlock')


class StcIpv6Group(StcIpGroup):
    """ Represents STC IPv6 group. """

    def __init__(self, **data):
        data['objType'] = 'Ipv4Group'
        super(self.__class__, self).__init__(**data)
        self.network_block = self.get_child('Ipv4NetworkBlock')
