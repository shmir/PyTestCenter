"""
This module implements classes and utility functions to manage STC port.

:author: yoram@ignissoft.com
"""
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

from trafficgenerator.tgn_utils import TgnError, is_local_host

from testcenter.stc_device import StcDevice
from testcenter.stc_object import StcObject
from testcenter.stc_stream import StcStream


class StcPort(StcObject):
    """Represent STC port."""

    def __init__(self, parent: Optional[StcObject], **data: str) -> None:
        data["objType"] = "port"
        super().__init__(parent, **data)
        self.generator = self.get_child("generator")
        self.capture = self.get_child("capture")
        self.location = None
        self.active_phy = None

    def get_devices(self) -> Dict[str, StcDevice]:
        """Returns all devices."""
        return {o.name: o for o in self.get_objects_or_children_by_type("EmulatedDevice")}

    devices = property(get_devices)

    def get_stream_blocks(self) -> Dict[str, StcStream]:
        """Returns all stream blocks."""
        return {o.name: o for o in self.get_objects_or_children_by_type("StreamBlock")}

    stream_blocks = property(get_stream_blocks)

    def reserve(self, location=None, force=False, wait_for_up=True, timeout=40) -> None:
        """Reserve physical port.

        :param location: port location in the form ip/slot/port.
        :param force: whether to revoke existing reservation (True) or not (False).
        :param wait_for_up: True - wait for port to come up, False - return immediately.
        :param timeout: how long (seconds) to wait for port to come up.

        :todo: seems like reserve takes forever even if port is already owned by the user.
            should test for ownership and take it forcefully only if really needed?
        """
        if location:
            self.location = location
            self.set_attributes(location=self.location)
        else:
            self.location = self.get_attribute("Location")

        if not is_local_host(self.location):
            self.api.perform("AttachPorts", PortList=self.ref, AutoConnect=True, RevokeOwner=force)
            self.api.apply()
            self.active_phy = StcObject(parent=self, objRef=self.get_attribute("activephy-Targets"))
            self.active_phy.get_attributes()
            if wait_for_up:
                self.wait_for_states(timeout, "UP")

    def wait_for_states(self, timeout: Optional[int] = 40, *states: str) -> None:
        """Wait until port reaches requested state(s).

        :param timeout: How long (seconds) to wait for port to come up.
        :param states: List of requested states.
        """
        link_state = None
        for _ in range(timeout):
            link_state = self.active_phy.get_attribute("LinkStatus")
            if link_state in states:
                return
            time.sleep(1)
        raise TgnError(f"Port failed to reach state {states}, port state is {link_state} after {timeout} seconds")

    def release(self) -> None:
        """Release the physical port reserved for the port."""
        if not is_local_host(self.location):
            self.api.perform("ReleasePort", portList=self.obj_ref())

    def is_online(self) -> bool:
        """Returns port link status."""
        return self.active_phy.get_attribute("LinkStatus").lower() == "up"

    def is_running(self) -> bool:
        """Returns running state of the port."""
        return self.generator.get_attribute("state") == "RUNNING"

    def send_arp_ns(self) -> None:
        """Send ARP/ND for the port."""
        StcObject.send_arp_ns(self)

    def get_arp_cache(self):
        """Send ARP/ND for the port."""
        return StcObject.get_arp_cache(self)

    def start(self, blocking=False):
        """Start port traffic.

        :param blocking: True - wait for traffic end. False - return immediately.
        """
        self.project.start_ports(blocking, self)

    def stop(self):
        """Stop port traffic."""
        self.project.stop_ports(self)

    def wait(self):
        """Wait for traffic end."""
        self.project.wait_traffic(self)

    def clear_results(self):
        """Clear all port results."""
        self.project.clear_results(self)

    def set_media_type(self, media_type):
        """Set media type for dual phy 1G ports.

        :param media_type: requested media type - EthernetCopper or EthernetFiber.
        """

        if media_type != self.active_phy.obj_type():
            new_phy = StcObject(parent=self, objType=media_type)
            self.set_targets(apply_=True, ActivePhy=new_phy.obj_ref())
            self.active_phy = new_phy

    def start_capture(self):
        """Start capture."""
        self.capture.api.perform("CaptureStart", CaptureProxyId=self.ref)

    def stop_capture(self):
        """Stop capture."""
        self.capture.api.perform("CaptureStop", CaptureProxyId=self.ref)

    def save_capture(self, capture_file: Path, start_frame: Optional[int] = 0, end_frame: Optional[int] = 0) -> None:
        """Save capture buffer to file.

        :param capture_file: Path to capture file.
        :param start_frame: First captured frame index to be saved.
        :param end_frame: Last captured frame index to be saved, if zero then save until the last captured frame..
        """
        self.capture.api.perform(
            "CaptureDataSave",
            CaptureProxyId=self.ref,
            FileName=capture_file.as_posix(),
            StartFrameIndex=start_frame,
            EndFrameIndex=end_frame,
        )

    #
    # Override inherited methods.
    #

    def get_name(self) -> str:
        """Get port name.

        Remove the 'offline' tag that STC adds to off lined ports..

        :returns: port name without the 'offline' tag added by STC.
        """
        return re.sub(r" \(offline\)$", "", self.get_attribute("Name"))

    def get_children(self, *types: str) -> List[StcObject]:
        """Get all port children including emulated devices.

        Special implementation since we want emulated devices under their port while in STC they are under project.

        Note: get_children() is not supported.
        """
        children_objects = []
        types = tuple(t.lower() for t in types)
        if "emulateddevice" in types:
            if not self.project.get_objects_by_type("emulateddevice"):
                self.project.get_children("emulateddevice")
            children_objects = self.get_objects_by_type("emulateddevice")
            types = tuple(t for t in types if t != "emulateddevice")
        if types:
            children_objects.extend(super(StcPort, self).get_children(*types))
        return children_objects


class StcGenerator(StcObject):
    """Represent STC port generator."""

    def __init__(self, **data):
        super().__init__(**data)
        self.config = self.get_child("GeneratorConfig")

    def get_attributes(self):
        """Get generator attribute from generatorConfig object."""
        return self.config.get_attributes()

    def set_attributes(self, apply_=False, **attributes):
        """Set generator attributes to generatorConfig object."""
        self.config.set_attributes(apply_=apply_, **attributes)


class StcAnalyzer(StcObject):
    """Represent STC port analyzer."""

    pass


class StcCapture(StcObject):
    """Represent STC capture."""

    pass


class StcLag(StcObject):
    """Represents STC LAG."""

    def __init__(self, parent: StcObject, **data: str) -> None:
        self.port = StcPort(parent, name=data["name"])
        data["objType"] = "lag"
        super().__init__(parent=self.port, **data)
        StcObject(objType="LacpGroupConfig", parent=self)

    def add_ports(self, *ports: StcPort) -> None:
        for stc_port in ports:
            self.append_attribute("PortSetMember-targets", stc_port.obj_ref())
            StcObject(objType="LacpPortConfig", parent=stc_port)
        self.api.apply()
