"""
This module implements classes and utility functions to manage STC chassis.

:author: yoram@ignissoft.com
"""

from collections import OrderedDict

from stc_object import StcObject


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
                children[child_name + child.get_attribute('Index')] = child
            setattr(self, child_var, children)
            for child in getattr(self, child_var).values():
                child.get_inventory()


class StcPhyChassis(StcPhyBase):

    attributes_names = ('Model', 'SerialNum', 'FirmwareVersion')
    children_types = {'modules': ('PhysicalTestModule', 'Slot ')}

    def get_thin_inventory(self):
        thin_inventory = OrderedDict()
        for module_name, module in self.modules.items():
            if module.attributes['Model']:
                thin_inventory[module_name] = module
                module.ports = OrderedDict()
                for pg in module.pgs.values():
                    module.ports.update(pg.ports)
        return thin_inventory


class StcPhyModule(StcPhyBase):

    attributes_names = ('Index', 'Model', 'Description', 'SerialNum', 'FirmwareVersion')
    children_types = {'pgs': ('PhysicalPortGroup', 'Port Group ')}


class StcPhyPortGroup(StcPhyBase):

    attributes_names = ('Index',)
    children_types = {'ports': ('PhysicalPort', 'Port ')}


class StcPhyPort(StcPhyBase):

    attributes_names = ('Index',)
    children_types = {}
