"""
This module implements classes and utility functions to manage STC streamblocks.

:author: yoram@ignissoft.com
"""

from typing import Optional

from testcenter.stc_object import StcObject


class StcStream(StcObject):
    """Represent STC stream block."""

    def __init__(self, parent: Optional[StcObject], **data: str) -> None:
        """Create new streamblock on STC.

        Remove automatically created Ethernet and IPv4 configurations under StreamBlock.

        :param parent: port object.
        """
        data["objType"] = "StreamBlock"
        super().__init__(parent, **data)

    def _create(self):
        sb_ref = super()._create()
        # Remove automatically created Ethernet and IPv4 configurations under StreamBlock.
        self.api.config(sb_ref, FrameConfig="")
        return sb_ref

    def send_arp_ns(self) -> None:
        StcObject.send_arp_ns(self)

    def get_arp_cache(self) -> list:
        return StcObject.get_arp_cache(self)


class StcGroupCollection(StcObject):
    """Represent STC group collection."""

    def __init__(self, **data) -> None:
        """Create new group collection on STC.

        :param name: group name.
        """
        data["objType"] = "GroupCollection"
        super().__init__(**data)

    def _create(self):
        gc_ref = super()._create()
        self.api.config(gc_ref, GroupName=self.obj_name())
        return gc_ref

    def get_name(self) -> str:
        return self.get_attribute("GroupName")


class StcTrafficGroup(StcObject):
    """Represent STC traffic group."""

    def __init__(self, **data) -> None:
        """Create new traffic group object.

        :param name: group name.
        :param parent: group collection object.
        """
        data["objType"] = "TrafficGroup"
        super().__init__(**data)

    def _create(self):
        tg_ref = super()._create()
        self.api.config(tg_ref, GroupName=self.obj_name())
        return tg_ref

    def get_name(self) -> str:
        return self.get_attribute("GroupName")

    def set_attributes(self, apply_=False, **attributes):
        for sb in self.get_stream_blocks():
            sb.set_attributes(apply_, **attributes)

    def get_stream_blocks(self) -> list:
        stream_blocks = self.get_list_attribute("AffiliationTrafficGroup-Targets")
        stc_sbs = [self.project.get_object_by_ref(r) for r in stream_blocks]
        if None in stc_sbs:
            self.project.get_stream_blocks()
            stc_sbs = [self.project.get_object_by_ref(r) for r in stream_blocks]
        return stc_sbs
