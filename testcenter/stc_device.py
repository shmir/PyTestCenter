"""
This module implements classes and utility functions to manage STC emulated device.
"""

from stc_object import StcObject


class StcDevice(StcObject):
    """ Represents STC emulated device. """

    # Create device under port (in STC objects tree emulateddevice is under project).
    def __init__(self, **data):
        """
        :param parent: when creating - port, when reading - project.
        """

        # Make sure parent is project.
        parent = data.pop('parent', None)
        data['parent'] = self.project

        # Create StcDevice object.
        data['objType'] = 'emulateddevice'
        super(StcDevice, self).__init__(**data)

        # If we create new device we should place it under the requested parent.
        if 'objRef' not in data:
            self.set_attributes(AffiliatedPort=parent.obj_ref())
            port = parent
        else:
            port = parent.get_object_by_ref(self.get_attribute('AffiliatedPort'))

        # Replace parent from project to parent.
        self._data['parent'] = port
        port.objects[self.obj_ref()] = self
        self.project.objects.pop(self.obj_ref())

    def command(self, command, wait_after=2, **arguments):
        self.project.command_devices(command, wait_after, self, **arguments)

    def send_arp_ns(self):
        StcObject.send_arp_ns(self)

    def get_arp_cache(self):
        return StcObject.get_arp_cache(self)

    def ping(self, ip):
        self.command('PingVerifyConnectivity', PingAddress=ip)
        self.test_command_rc('PassFailState')

    def start(self, wait_after=4):
        self.command('DeviceStart', wait_after)
        self.test_command_rc('Status')

    def stop(self, wait_after=4):
        self.command('DeviceStop', wait_after)
        self.test_command_rc('Status')

    def command_emulations(self, command, wait_after=4, **arguments):
        self.project.command_device_emulations(command, wait_after, self, **arguments)

    def get_ordered_valns(self):
        if not self.get_objects_or_children_by_type('VlanIf'):
            return []
        stc_eth = self.get_objects_or_children_by_type('EthIIIf')[0]
        stc_next_if_ref = stc_eth.get_attribute('StackedOnEndpoint-sources')
        stc_next_if = self.get_object_by_ref(stc_next_if_ref)
        stc_vlans = []
        while stc_next_if and stc_next_if.obj_type() == 'VlanIf':
            stc_vlans.append(stc_next_if)
            stc_next_if_ref = stc_next_if.get_attribute('StackedOnEndpoint-sources')
            stc_next_if = self.get_object_by_ref(stc_next_if_ref)
        return stc_vlans


class StcEmulation(StcObject):
    """ Base class for all STC emulations. """

    def command(self, command, wait_after=4, **arguments):
        """ Perform """
        self.project.command_emulations(command, wait_after, self, **arguments)


class StcRouter(StcEmulation):
    objects_list = 'RouterList'


class StcClient(StcEmulation):
    objects_list = 'BlockList'


class StcServer(StcEmulation):
    objects_list = 'ServerList'


class StcOspfv2Router(StcRouter):
    pass


class StcBgpRouter(StcRouter):
    pass


class StcBgpRoute(StcObject):

    def get_network_block(self):
        return self.get_objects_by_type_in_subtree(None, 'ipv4networkblock', 'ipv6networkblock')[0]


class StcRouterLsa(StcObject):

    def get_network_block(self):
        return self.get_objects_by_type_in_subtree(None, 'ipv4networkblock', 'ipv6networkblock')[0]


class StcPimRouter(StcRouter):
    pass


class StcPimv4Group(StcObject):

    def get_network_block(self):
        stc_group = self.project.get_object_by_ref(self.get_attribute('JoinedGroup-targets'))
        return stc_group.network_block


class StcIgmpHost(StcClient):
    pass


class StcIgmpGroup(StcObject):

    def get_network_block(self):
        return self.get_objects_by_type_in_subtree(None, 'ipv4networkblock', 'ipv6networkblock')[0]


class StcIgmpQuerier(StcClient):
    pass


class StcOseSwitch(StcEmulation):
    objects_list = 'HandleList'


class StcIsisRouter(StcRouter):
    pass
