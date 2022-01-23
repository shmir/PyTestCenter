"""
Base classes and utilities to manage Spirent Test Center (STC).

:author: yoram@ignissoft.com
"""
from __future__ import annotations

import re
import time
from collections import OrderedDict
from typing import List, Optional, Union

from trafficgenerator.tgn_object import TgnObject
from trafficgenerator.tgn_tcl import build_obj_ref_list
from trafficgenerator.tgn_utils import TgnError

import testcenter
from testcenter.api.stc_rest import StcRestWrapper


def extract_stc_obj_type_from_obj_ref(obj_ref: str) -> str:
    """Extract object type from object reference.

    :param obj_ref: object reference.
    """
    # There are rare cases where object reference has no sequential number suffix like 'automationoptions'.
    match = re.search(r"(.*\D+)\d+", obj_ref)
    return match.group(1) if match else obj_ref


class StcObject(TgnObject):
    """Base class for all STC objects."""

    str_2_class = {}

    project: Optional[testcenter.stc_project.StcProject] = None

    def __init__(self, parent: Union[StcObject, None], **data: str) -> None:
        if "objRef" in data:
            data["objType"] = extract_stc_obj_type_from_obj_ref(data["objRef"])
            if not parent and data["objType"] != "system":
                self._data["objRef"] = data["objRef"]
                parent = self.get_object_from_attribute("parent")
        if type(self) == StcObject:
            self.__class__ = self.get_obj_class(data["objType"])
        super().__init__(parent, **data)

    def get_obj_class(self, obj_type: str) -> StcObject:
        """Returns object class if specific class else StcObject.

        :param obj_type: STC object type.
        """
        return StcObject.str_2_class.get(obj_type.lower(), StcObject)

    def _create(self) -> str:
        """Create new object on STC."""
        # At this time objRef is not set yet so we must use direct calls to api.
        attributes = dict(self._data)
        attributes.pop("objType")
        attributes.pop("parent")
        if "name" in self._data:
            return self.api.create(self.type, self.parent, **attributes)
        else:
            stc_obj = self.api.create(self.type, self.parent, **attributes)
            self._data["name"] = self._get_name(self.api.get(stc_obj, "name"), stc_obj)
            return stc_obj

    def command(self, command, wait_after=0, **arguments):
        rc = self.api.perform(command, **arguments)
        time.sleep(wait_after)
        return rc

    def get_attribute(self, attribute):
        """Get single attribute value.

        :param attribute: attribute name.
        :return: attribute value.
        """
        return self.api.get(self.ref, attribute)

    def get_list_attribute(self, attribute):
        """
        :return: attribute value as Python list.
        """
        return self.api.getList(self.obj_ref(), attribute)

    def get_objects_from_attribute(self, attribute):
        objects = []
        for handle in self.get_attribute(attribute).split():
            obj = self.project.get_object_by_ref(handle)
            if not obj:
                obj = StcObject(objRef=handle, parent=self)
            objects.append(obj)
        return objects

    def append_attribute(self, attribute, value, apply_=False):
        cur_value = self.api.get(self.obj_ref(), attribute)
        attributes = {attribute: cur_value + " " + str(value)}
        self.set_attributes(apply_=apply_, **attributes)

    def get_attributes(self, *attributes):
        """Get multiple attributes values.

        Some low level APIs (like Tcl over Telnet) supports limited output length.
        When using get_attributes() the method will use simple stc::get to read all attributes. This is efficient but
        the output might exceed the output limit and will be truncated.
        When using attributes(*attributes) the method will use stc::get -attribute to read the attributes one by one.
        This is less efficient but less likely to exceed the output length.

        :param attributes: list of attributes to retrieve. If empty (default) return all attribute values.
        :return: dictionary {attribute: value} of all requested attributes.
        """

        if not attributes:
            if isinstance(self.api, StcRestWrapper):
                attributes = self.api.get(self.ref).split()
            else:
                return self.api.get(self.ref)
        values = {}
        for attribute in attributes:
            values[attribute] = self.get_attribute(attribute)
        return values

    def get_children(self, *types: str) -> List[StcObject]:
        """Get list of all children of the object.

        :param types: get only children of type in types, if types not specified, get all children.
        """
        children_objects = OrderedDict()
        if not types:
            types = self.get_all_child_types()
        for child_type in types:
            output = self.get_attribute("children" + "-" + child_type)
            children_objects.update(self._build_children_objs(child_type, output.split(" ")))
        return list(children_objects.values())

    def get_all_child_types(self):
        children = self.get_attribute("children").split()
        return list(set([m.group(1) for c in children for m in [re.search(r"(.*\D+)\d+", c)]]))

    def set_attributes(self, apply_=False, **attributes):
        self.api.config(self.ref, **attributes)
        if apply_:
            self.api.apply()

    def set_attributes_serializer(self, _apply, attributes):
        """Set attributes from serialized key value dictionary."""

        self.api.config(self.obj_ref(), **attributes)
        if _apply:
            self.api.apply()

    def set_active(self, active):
        self.set_attributes(Active=active)

    def set_targets(self, apply_=False, **attributes):
        attributes_targets = {}
        for attribute, value in attributes.items():
            attributes_targets[attribute + "-targets"] = value
        self.set_attributes(apply_, **attributes_targets)

    def set_sources(self, apply_=False, **attributes):
        attributes_targets = {}
        for attribute, value in attributes.items():
            attributes_targets[attribute + "-sources"] = value
        self.set_attributes(apply_, **attributes_targets)

    def delete(self):
        self.api.delete(self.ref)
        self.del_object_from_parent()

    def get_name(self):
        self._data["name"] = self._get_name(self.get_attribute("Name"), self.obj_ref())
        return self._data["name"]

    def get_active(self):
        return self.get_attribute("Active")

    def test_command_rc(self, attribute):
        status = self.api.command_rc[attribute].lower()
        if status and "passed" not in status and "successful" not in status:
            raise TgnError(f"{attribute} = {status}")

    def wait(self):
        """Wait until sequencer is finished."""
        self.api.wait()

    @classmethod
    def send_arp_ns(cls, *objects: StcObject) -> None:
        """Send ARP and NS for ports, devices or stream blocks."""
        objects[0].api.perform("ArpNdStart", HandleList=build_obj_ref_list(list(objects)))

    @classmethod
    def get_arp_cache(cls, *objects):
        arp_table = []
        for obj in objects:
            obj.command("ArpNdUpdateArpCache", HandleList=obj.obj_ref())
            arp_cache = obj.get_child("ArpCache")
            arp_table += arp_cache.get_list_attribute("ArpCacheData")
        return arp_table

    def _get_name(self, read_name, obj_ref):
        name = read_name
        if read_name.replace(" ", "").lower() == obj_ref:
            name = self.obj_parent().obj_name() + "/" + self.obj_type()
        return name
