"""
This module implements classes and utility functions to manage STC chassis.

:author: yoram@ignissoft.com
"""

import re
from collections import OrderedDict

from testcenter.stc_object import StcObject


class StcHw(StcObject):
    """ Represent STC port. """

    def get_chassis(self, hostname):
        for chassis in self.get_children('PhysicalChassis'):
            if chassis.get_attribute('Hostname') == hostname:
                return chassis
        connect_rc = self.api.perform('ChassisConnect', Hostname=hostname)
        return StcPhyChassis(parent=self, objRef=connect_rc['OutputChassisList'])


class StcPhyBase(StcObject):

    def get_inventory(self):
        self.attributes = self.get_attributes(*self.attributes_names)
        for child_var, child_type_name in self.children_types.items():
            child_type, child_name = child_type_name
            children = OrderedDict()
            for child in self.get_objects_or_children_by_type(child_type):
                # Ignore empty slots.
                if type(child) is StcPhyModule and not child.get_attribute('Description'):
                    continue
                children[child_name + child.get_attribute('Index')] = child
            setattr(self, child_var, children)
            for child in getattr(self, child_var).values():
                child.get_inventory()


class StcPhyChassis(StcPhyBase):

    attributes_names = ('Model', 'SerialNum', 'FirmwareVersion')
    children_types = {'modules': ('PhysicalTestModule', 'Slot ')}

    pss = {}

    def get_inventory(self):
        super(self.__class__, self).get_inventory()

        self.pss = {}
        ps_status = self.get_child('PhysicalChassisPowerSupplyStatus')
        power_supply_list = ps_status.get_list_attribute('PowerSupplyList')
        power_supply_status_list = ps_status.get_list_attribute('PowerSupplyStatusList')
        for name, status in zip(power_supply_list, power_supply_status_list):
            # name can be 'slot-n' (e.g. 4.52) or 'n' (e.g. 4.70). BUG? waiting for Spirent response.
            if len(name.split('-')) < 2:
                continue
            index = name.split('-')[1]
            if status != 'POWER_STATUS_NOT_PRESENT':
                if name.startswith('chs'):
                    self.pss['Power ' + index] = StcPhyPowerSupply(index, status)
                else:
                    if self.get_module_by_index(index):
                        self.get_module_by_index(index).ps = StcPhyPowerSupply(index, status)

    def get_thin_inventory(self):
        thin_inventory = OrderedDict()
        for module_name, module in self.modules.items():
            if module.attributes['Model']:
                thin_inventory[module_name] = module
                module.ports = OrderedDict()
                for pg in module.pgs.values():
                    module.ports.update(pg.ports)
        return thin_inventory

    def get_module_by_index(self, index):
        for module in self.modules.values():
            if module.attributes['Index'] == index:
                return module


class StcPhyModule(StcPhyBase):

    attributes_names = ('Index', 'Model', 'Description', 'SerialNum', 'FirmwareVersion')
    children_types = {'pgs': ('PhysicalPortGroup', 'Port Group ')}

    ps = None

    def get_inventory(self):
        super(self.__class__, self).get_inventory()

        supported_speeds = self.command('spirent.core.GetSupportedSpeedsCommand', PhyTestModule=self.obj_ref())
        self.attributes['SupportedSpeeds'] = re.findall(r'([0-9.]*[M|G]):', supported_speeds['SpeedInfoList'])


class StcPhyPortGroup(StcPhyBase):

    attributes_names = ('Index', 'TestPackage')
    children_types = {'ports': ('PhysicalPort', 'Port ')}


class StcPhyPort(StcPhyBase):

    attributes_names = ('Index',)
    children_types = {}


class StcPhyPowerSupply(object):

    def __init__(self, index, status):
        self.attributes = {'Index': index,
                           'Status': status}
