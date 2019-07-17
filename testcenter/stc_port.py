"""
This module implements classes and utility functions to manage STC port.

:author: yoram@ignissoft.com
"""

import re
import time
from enum import Enum
from collections import OrderedDict

from trafficgenerator.tgn_utils import is_local_host, TgnError
from testcenter.stc_object import StcObject
from testcenter.stc_stream import StcStream


class PORT_TRANSMIT_MODES(Enum):
    MANUAL_BASED = 0
    STREAM_BASED = 1
    PORT_BASED = 2

class StcManualSchedule(StcObject):
    def __init__(self, **data):
        data['objType'] = 'ManualSchedule'
        super(StcManualSchedule, self).__init__(**data)

class StcManualScheduleEntry(StcObject):
    def __init__(self, **data):
        data['objType'] = 'ManualScheduleEntry'
        super(StcManualScheduleEntry, self).__init__(**data)

class StcStreamBlockLoadProfile(StcObject):
    def __init__(self, **data):
        data['objType'] = 'StreamBlockLoadProfile'
        super(StcStreamBlockLoadProfile, self).__init__(**data)

class StcPort(StcObject):
    """ Represent STC port. """

    def __init__(self, **data):
        data['objType'] = 'port'
        super(StcPort, self).__init__(**data)
        self.generator = self.get_child('generator') #type: StcGenerator
        self.analyzer = self.get_child('analyzer') #type: StcAnalyzer
        self.streams = OrderedDict()
        self._location = None
        self.transmit_mode = None
        self._activephy = None


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

    def add_stream(self, name=None):
        if not name:
            sCount = len(self.get_stream_blocks())
            name = 's_'+str(sCount)
        self.streams[name] = StcStream(parent=self, name=name)
        if self.transmit_mode == 'RATE_BASED':
            lp = StcStreamBlockLoadProfile(parent=self.project)
            self.streams[name].set_attributes(AffiliationStreamBlockLoadProfile=lp.ref)
        elif self.transmit_mode =='MANUAL_BASED':
            ms = StcManualSchedule(parent=self.generator.config)
            mse = StcManualScheduleEntry(parent=ms)
            mse.set_attributes(StreamBlock=self.streams[name].ref)
        elif self.transmit_mode == 'PORT_BASED':
            pass
        return self.streams[name]

    def _update_manual_schedule_streams(self):
        ms = StcManualSchedule(parent=self.generator.config)
        for name in self.streams:
            mse = StcManualScheduleEntry(parent=ms)
            mse.set_attributes(StreamBlock=self.streams[name].ref)

    def trasmit_mode(self,transmit_mode):
        if transmit_mode == 'MANUAL_BASED':
            self.transmit_mode = 'MANUAL_BASED'
            self._update_manual_schedule_streams()
        elif transmit_mode == 'PORT_BASED':
            self.transmit_mode = 'PORT_BASED'
        elif transmit_mode == 'RATE_BASED':
            self.transmit_mode = 'RATE_BASED'
        self.generator.config.set_attributes(SchedulingMode=transmit_mode)

    @property
    def ignore_link_status(self):
        return self.activephy.get_attributes('IgnoreLinkStatus')

    @ignore_link_status.setter
    def ignore_link_status(self,ignore):
        self.activephy.set_attributes(IgnoreLinkStatus=ignore)

    @property
    def loopback(self):
        return False if self.activephy.get_attributes('DataPathMode') is 'Normal' else True

    @loopback.setter
    def loopback(self,mode):
        lb_mode = 'Normal' if mode is False else 'LOCAL_LOOPBACK'
        self.activephy.set_attributes(DataPathMode=lb_mode)


    def wait_for_up(self,timeout=40):
        self.wait_for_states(timeout, 'UP', 'DOWN', 'ADMIN_DOWN')


    def reserve(self, location=None, force=False, wait_for_up=True, timeout=40):
        """ Reserve physical port.

        :param location: port location in the form ip/slot/port.
        :param force: whether to revoke existing reservation (True) or not (False).
        :param wait_for_up: True - wait for port to come up, False - return immediately.
        :param timeout: how long (seconds) to wait for port to come up.

        :todo: seems like reserve takes forever even if port is already owned by the user.
            should test for ownership and take it forcefully only if really needed?
        """

        if location:
            self.location = location
            #self.set_attributes(location=self.location)
        else:
            self._location = self.get_attribute('Location')

        if not is_local_host(self.location):
            self.api.perform('AttachPorts', PortList=self.obj_ref(), AutoConnect=True, RevokeOwner=force)
            self.api.apply()
            self._get_phy()
            if wait_for_up:
                self.wait_for_states(timeout, 'UP', 'DOWN', 'ADMIN_DOWN')

    def reset_to_default(self):
        pass
        # stc::perform
        # ResetConfig - config
        # system1


    @property
    def activephy(self):
        if not self._activephy:
            self._activephy = StcObject(parent=self, objRef=self.get_attribute('activephy-Targets'))
            self._activephy.get_attributes()
        return self._activephy

    @activephy.setter
    def activephy(self,phy):
        self._activephy = phy


    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location
        self.set_attributes(location=location)

    @property
    def tx_stats(self):
        return self.generator.stats

    @property
    def rx_stats(self):
        return self.analyzer.stats

    def wait_for_states(self, timeout=40, *states):
        """ Wait until port reaches requested state(s).

        :param timeout: how long (seconds) to wait for port to come up.
        :param states: list of requested states.
        """

        for _ in range(timeout):
            if self.activephy.get_attribute('LinkStatus') in states:
                return
            time.sleep(1)
        raise TgnError('Failed to reserve port, port is {} after {} seconds'.
                       format(self.activephy.get_attribute('LinkStatus'), timeout))

    def release(self):
        """ Release the physical port reserved for the port. """

        if not is_local_host(self.location):
            self.api.perform('ReleasePort', portList=self.obj_ref())

    def reset(self):
        self.clear_streams()
        self.api.perform('ResetConfig', config=self.ref)
        #self.clear_results() ??
        self.api.apply()
        pass

    def clear_streams(self):
        self.streams = OrderedDict()
        self.del_objects_by_type('stream')

    def is_online(self):
        """
        :returns: Port link status.
                  True - port is up.
                  False - port is offline.
        """

        return self.activephy.get_attribute('LinkStatus').lower() == 'up'

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
        return re.sub(' \(offline\)$', '', self.get_attribute('Name'))

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
        self._stats = None

    def get_attributes(self):
        """ Get generator attribute from generatorConfig object. """
        return self.config.get_attributes()

    def set_attributes(self, apply_=False, **attributes):
        """ Set generator attributes to generatorConfig object. """
        self.config.set_attributes(apply_=apply_, **attributes)

    @property
    def stats(self):
        if not self._stats:
            self._stats = StcGeneratorStats(self.parent)
        return self._stats.counters

class StcAnalyzer(StcObject):
    """ Represent STC port analyzer. """
    def __init__(self, **data):
        super(self.__class__, self).__init__(**data)
        self._stats = None

    @property
    def stats(self):
        if not self._stats:
            self._stats = StcAnalyzerStats(self.parent)
        return self._stats.counters


class StcLag(StcObject):
    """ Represents STC LAG. """

    def __init__(self, **data):
        self.port = StcPort(name=data['name'], parent=data['parent'])
        data['objType'] = 'lag'
        data['parent'] = self.port
        super(self.__class__, self).__init__(**data)
        StcObject(objType='LacpGroupConfig', parent=self)

    def add_ports(self, *ports):
        for stc_port in ports:
            self.append_attribute('PortSetMember-targets', stc_port.obj_ref())
            StcObject(objType='LacpPortConfig', parent=stc_port)
        self.api.apply()

class StcPortStats(object):
    def __init__(self,parent,config_type,result_type):
        super(StcPortStats, self).__init__()
        self.parent = parent
        self._stats = self.subscribe(config_type, result_type)

    def subscribe(self,config_type,result_type):
        rds = self.parent.api.subscribe(Parent=self.parent.project.ref, ResultParent=self.parent.ref,
                                 ConfigType=config_type, ResultType=result_type)
        return StcObject(objType='ResultDataSet', parent=self.parent, objRef=rds)

    @property
    def counters(self):
        res = self._stats.get_objects_from_attribute('ResultHandleList')[0].get_attributes()
        #TODO pop nonstat members
        return dict(zip(res.keys(), res.values()))


class StcGeneratorStats(StcPortStats):
    def __init__(self,parent):
        super(StcGeneratorStats, self).__init__(parent,'generator','generatorPortResults')


class StcAnalyzerStats(StcPortStats):
    def __init__(self,parent):
        super(StcAnalyzerStats, self).__init__(parent,'analyzer','AnalyzerPortResults')

