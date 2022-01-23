"""
TestCenter package tests that can run in offline mode.

@author yoram@ignissoft.com
"""
import inspect
import logging
from pathlib import Path

import pytest

from testcenter.api.stc_rest import StcRestWrapper
from testcenter.stc_app import StcApp
from testcenter.stc_device import StcDevice
from testcenter.stc_object import StcObject
from testcenter.stc_port import StcPort
from testcenter.stc_stream import StcStream


def test_hello_world(stc: StcApp) -> None:
    """Just make sure the setup is up and running."""
    assert stc


def test_load_config(logger: logging.Logger, stc: StcApp) -> None:
    """Load existing configuration."""
    logger.info(test_load_config.__doc__.strip())

    configs_dir = Path(__file__).parent.joinpath("configs")
    config_file = configs_dir.joinpath("test_config.xml")
    stc.load_config(config_file.as_posix())
    temp_dir = configs_dir.joinpath("temp")
    config_file_save = temp_dir.joinpath(f"{config_file.stem}-save{config_file.suffix}")
    stc.save_config(config_file_save.as_posix())

    with pytest.raises(Exception):
        stc.load_config(configs_dir.joinpath("tcc.invalid").as_posix())
    with pytest.raises(Exception):
        stc.load_config(configs_dir.joinpath("invalid.tcc").as_posix())


def test_analyze_config(logger: logging.Logger, stc: StcApp) -> None:
    """Analyze existing configuration."""
    logger.info(test_analyze_config.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath("configs").joinpath("test_config.xml").as_posix())

    stc.project.get_children("port")
    port1_obj = stc.project.get_object_by_name("Port 1")
    port2_obj = stc.project.get_object_by_name("Port 2")

    print(f"Port1 object reference = {port1_obj.ref}")
    print(f"Port1 name = {port1_obj.name}")
    print(f'Ports = {stc.project.get_objects_by_type("port")}')
    print(f'Port 1 state = {port1_obj.get_attribute("Location")}')
    print(f"Port 1 attributes = {port1_obj.get_attributes()}")
    print(f'Port 1 streamblocks = {port1_obj.get_children("streamblock")}')
    print(f'Port 2 streamblocks = {port2_obj.get_children("streamblock")}')

    stc_ports = stc.project.get_children("port")
    assert len(stc_ports) == 2

    assert len(stc_ports[0].get_children("emulateddevice")) == 1
    assert len(stc_ports[1].get_children("emulateddevice")) == 1

    assert len(stc.project.get_devices()) == 2
    assert len(stc.project.get_devices(stc_ports[0])) == 1
    assert len(stc.project.get_devices(stc_ports[1])) == 1

    assert len(stc.project.get_children("GroupCollection")) == 1
    assert len(stc.project.get_object_by_name("TG 1").get_children("TrafficGroup")) == 1
    assert len(stc.project.get_object_by_name("TG 1").get_object_by_name("SG 1").get_stream_blocks()) == 2
    assert len(stc.project.get_stream_blocks()) == 2


def test_children(logger: logging.Logger, stc: StcApp) -> None:
    """Test specific get children methods."""
    logger.info(test_children.__doc__)

    stc.load_config(Path(__file__).parent.joinpath("configs").joinpath("test_config.xml").as_posix())

    assert len(stc.project.ports) == 2
    for port in stc.project.ports.values():
        assert len(port.devices) == 1
        assert len(port.stream_blocks) == 1


def test_build_config(logger: logging.Logger, stc: StcApp) -> None:
    """Build simple config from scratch."""
    logger.info(test_build_config.__doc__.strip())

    for port_name in ("Port 1", "Port 2"):
        logger.info('Create Port "%s"', port_name)
        stc_port = StcPort(name=port_name, parent=stc.project)

        for dev_name in (port_name + " Device 1", port_name + " Device 2"):
            logger.info('Build Device "%s"', dev_name)
            stc_dev = StcDevice(name=dev_name, parent=stc_port)
            stc_eth = StcObject(objType="EthIIIf", parent=stc_dev)
            stc_eth.set_attributes(SourceMac="00:11:22:33:44:55")
            stc_dev.set_attributes(TopLevelIf=stc_eth.ref, PrimaryIf=stc_eth.ref)
            # stc_ip = StcObject(objType="Ipv4If", parent=stc_dev)
            # stc_ip.set_attributes(Address="1.2.3.4", PrefixLength=16)

        for sb_name in (port_name + " StreamBlock 1", port_name + " StreamBlock 2"):
            logger.info('Build StreamBlock "%s"', sb_name)
            stc_sb = StcStream(name=sb_name, parent=stc_port)
            stc_eth = StcObject(objType="ethernet:ethernetii", parent=stc_sb)
            stc_eth.set_attributes(DstMac="00:10:20:30:40:50")

    stc_ports = stc.project.get_children("port")
    assert len(stc_ports) == 2
    for stc_port in stc_ports:
        assert len(stc_port.get_children("generator")) == 1
        assert len(stc_port.get_children("generator", "analyzer")) == 2
        assert len(stc_port.get_children("emulateddevice")) == 2
        assert len(stc_port.get_children("emulateddevice", "generator", "analyzer")) == 4
    for stc_port in stc_ports:
        assert len(stc_port.get_children("streamblock")) == 2

    stc.api.apply()

    test_name = inspect.stack()[0][3]
    stc.save_config(Path(__file__).parent.joinpath("configs/temp", test_name + ".tcc").as_posix())


def test_stream_under_project(logger: logging.Logger, stc: StcApp) -> None:
    """Build simple config with ports under project object."""
    logger.info(test_stream_under_project.__doc__.strip())

    for port_name in ("Port 1", "Port 2"):
        logger.info(f'Create Port "{port_name}"')
        stc_port = StcPort(name=port_name, parent=stc.project)

        for sb_name in (port_name + " StreamBlock 1", port_name + " StreamBlock 2"):
            logger.info(f'Build StreamBlock "{sb_name}"')
            stc_sb = StcStream(name=sb_name, parent=stc_port)
            stc_eth = StcObject(objType="ethernet:ethernetii", parent=stc_sb)
            stc_eth.set_attributes(DstMac="00:10:20:30:40:50")

    test_name = inspect.stack()[0][3]
    stc.save_config(Path(__file__).parent.joinpath("configs/temp", test_name + ".tcc").as_posix())


def test_build_emulation(logger: logging.Logger, stc: StcApp) -> None:
    """Build simple BGP configuration."""
    logger.info(test_build_emulation.__doc__.strip())

    stc_port = StcPort(name="Port 1", parent=stc.project)
    stc_dev = StcDevice(name="Device 1", parent=stc_port)
    stc_eth = StcObject(objType="EthIIIf", parent=stc_dev)
    stc_eth.set_attributes(SourceMac="00:11:22:33:44:55")
    stc_ip = StcObject(objType="Ipv4If", parent=stc_dev)
    stc_ip.set_attributes(Address="1.2.3.4", PrefixLength=16)
    StcObject(objType="BgpRouterConfig", parent=stc_dev)

    test_name = inspect.stack()[0][3]
    stc.save_config(Path(__file__).parent.joinpath("configs/temp", test_name + ".tcc").as_posix())


def test_backdoor(stc: StcApp) -> None:
    """Test direct access to stcrestclient."""
    if not isinstance(stc.api, StcRestWrapper):
        pytest.skip("Skip tests - non rest API")

    print(stc.api.client.get(stc.project.ref, "children").split())
    print(stc.api.client.get(stc.project.ref, "children-port").split())

    stc.load_config(Path(__file__).parent.joinpath("configs").joinpath("test_config.xml").as_posix())
    ports = stc.api.client.get(stc.project.ref, "children-port").split()

    print(stc.api.client.get(ports[0]))
    print(stc.api.client.get(ports[0], "Name"))
    print(stc.api.client.get(ports[0], "Name", "Active"))

    print(stc.api.client.config(ports[0], Name="New Name", Active=False))
    print(stc.api.client.get(ports[0], "Name", "Active"))
