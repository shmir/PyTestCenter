"""
This module implements classes and utility functions to manage STC port.

:author: yoram@ignissoft.com
"""

import re
import time

from trafficgenerator.tgn_utils import is_local_host, TgnError

from stc_object import StcObject


class StcPort(StcObject):
    """ Represent STC port. """

    def __init__(self, **data):
        data['objType'] = 'port'
        data['parent'] = self.project
        super(self.__class__, self).__init__(**data)
        self.generator = self.get_child('generator')

    def get_devices(self):
        """
        :return: dictionary {name: object} of all emulated devices.
        """

        return {o.obj_name(): o for o in self.get_objects_or_children_by_type('EmulatedDevice')}

    def get_stream_blocks(self):
        """
        :return: dictionary {name: object} of all streams.
        """

        return {o.obj_name(): o for o in self.get_objects_or_children_by_type('StreamBlock')}

    def reserve(self, location, force=False, wait_for_up=True):
        """ Reserve physical port.

        :param location: port location in the form ip/slot/port.
        :param force: whether to revoke existing reservation (True) or not (False).
        :todo: seems like reserve takes forever even if port is already owned by the user.
            should test for ownership and take it forcefully only if really needed.
        """

        self._location = location
        self.set_attributes(location=location)
        if not is_local_host(location):
            self.api.perform('AttachPorts', PortList=self.obj_ref(), AutoConnect=True, RevokeOwner=force)
            self.api.apply()
            self.activephy = StcObject(parent=self, objRef=self.get_attribute('activephy-Targets'))
            self.activephy.get_attributes()
            if wait_for_up:
                self.wait_for_states(40, 'UP', 'DOWN', 'ADMIN_DOWN')

    def wait_for_states(self, timeout=40, *states):
        for _ in range(timeout):
            if self.activephy.get_attribute('LinkStatus') in states:
                return
            time.sleep(1)
        raise TgnError('Failed to reserve port, port is {} after {} seconds'.
                       format(self.activephy.get_attribute('LinkStatus'), timeout))

    def release(self):
        """ Release the physical port reserved for the port. """
        if not is_local_host(self._location):
            self.api.perform('ReleasePort', portList=self.obj_ref())

    def is_online(self):
        """
        :returns: Port link status.
                  True - port is up.
                  False - port is offline.
        """

        return self.activephy.get_attribute('linkstatus').lower() == 'up'

    def is_running(self):
        """
        :returns: Returns running state of the port.
                  True -- port is running.
                  False -- port is not running.
        """
        return self.generator.get_attribute('state') == 'RUNNING'

    def send_arp_ns(self):
        """ Send ARP/ND for the port. """
        StcObject.send_arp_ns(self)

    def get_arp_cache(self):
        """ Send ARP/ND for the port. """
        return StcObject.get_arp_cache(self)

    def start(self, blocking=False):
        """ Start port traffic.

        :param blocking: True - wait for traffic end. False - return immidately.
        """
        self.project.start_ports(blocking, self)

    def stop(self):
        """ Stop port traffic. """
        self.project.stop_ports(self)

    def wait(self):
        """ Wait for traffic end. """
        self.project.wait_traffic(self)

    def clear_results(self):
        """ Clear all port results. """
        self.project.clear_results(self)

    def set_media_type(self, media_type):
        """ Set media type for dual phy 1G ports.

        :param media_type: requested media type - EthernetCopper or EthernetFiber.
        """

        if media_type != self.activephy.obj_type():
            new_phy = StcObject(parent=self, objType=media_type)
            self.set_targets(apply_=True, ActivePhy=new_phy.obj_ref())
            self.activephy = new_phy

    #
    # Override inherited methods.
    #

    # Special implementation since we want to remove the 'offile' tag that STC adds even if the
    # 'Append Location to Name' check-box is unchecked.
    def get_name(self):
        """
        :returns: port name without the 'offilne' tag added by STC.
        """
        return re.sub(' \(offline\)$', '', super(StcPort, self).get_name())

    # Special implementation since we want emulateddevices under their port while in STC they are
    # under project.
    def get_children(self, *types):
        """ Get all port children including emulateddevices.

        Note: get_children() is not supported.
        """
        children_objs = []
        types = tuple(t.lower() for t in types)
        if 'emulateddevice' in types:
            if not self.project.get_objects_by_type('emulateddevice'):
                self.project.get_children('emulateddevice')
            children_objs = self.get_objects_by_type('emulateddevice')
            types = tuple(t for t in types if t != 'emulateddevice')
        if types:
            children_objs.extend(super(StcPort, self).get_children(*types))
        return children_objs


class StcGenerator(StcObject):
    """ Represent STC port generator. """

    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self.config = self.get_child('GeneratorConfig')

    def get_attributes(self):
        """ Get generator attribute from generatorConfig object. """
        return self.config.get_attributes()

    def set_attributes(self, apply_=False, **attributes):
        """ Set generator attributes to generatorConfig object. """
        self.config.set_attributes(apply_=apply_, **attributes)


class StcAnalyzer(StcObject):
    """ Represent STC port analyzer. """

    pass


class StcLag(StcObject):
    """ Represents STC LAG. """

    def __init__(self, **data):
        self.port = StcPort(name=data['name'])
        data['objType'] = 'lag'
        data['parent'] = self.port
        super(self.__class__, self).__init__(**data)
        StcObject(objType='LacpGroupConfig', parent=self)

    def add_ports(self, *ports):
        for stc_port in ports:
            self.append_attribute('PortSetMember-targets', stc_port.obj_ref())
            StcObject(objType='LacpPortConfig', parent=stc_port)
        self.api.apply()
