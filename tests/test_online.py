"""
TestCenter package tests that require actual TestCenter chassis and active ports.

Test setup:
Two STC ports connected back to back.

@author yoram@ignissoft.com
"""
import logging
from pathlib import Path
from typing import List

from testcenter.stc_app import StcApp
from testcenter.stc_statistics_view import StcStats
from testcenter.stc_app import StcSequencerOperation


def test_inventory(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Get inventory and test some basic info. """
    logger.info(test_inventory.__doc__.strip())

    chassis = stc.hw.get_chassis(locations[0].split('/')[0])
    chassis.get_inventory()
    assert len(chassis.modules) >= 1
    for module in chassis.modules.values():
        assert len(module.pgs) >= 1
        for pg in module.pgs.values():
            assert len(pg.ports) >= 1


def test_online(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Load configuration on ports and verify that ports are online. """
    logger.info(test_online.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('test_config.xml').as_posix())
    reserve_ports(stc, locations, wait_for_up=True)

    for port in stc.project.ports.values():
        assert port.is_online()

    for port in stc.project.ports.values():
        port.release()

    stc.project.get_object_by_name('Port 1').reserve(wait_for_up=False)
    stc.project.get_object_by_name('Port 2').reserve(wait_for_up=False)


def test_arp(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Test ARP commands. """
    logger.info(test_arp.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('test_config.xml').as_posix())
    reserve_ports(stc, locations, wait_for_up=True)

    stc.send_arp_ns()
    for port in stc.project.ports.values():
        port.send_arp_ns()
        for device in port.get_children('emulateddevice'):
            device.send_arp_ns()
        for sb in port.get_children('streamblock'):
            sb.send_arp_ns()


# If this test fails, consider adding delay between ping commands.
def test_ping(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Test Ping commands. """
    logger.info(test_ping.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('test_config.xml').as_posix())
    reserve_ports(stc, locations, wait_for_up=True)

    stc.send_arp_ns()
    for port in stc.project.ports.values():
        for device in port.get_children('emulateddevice'):
            gateway = device.get_child('ipv4if', 'ipv6if').get_attribute('Gateway')
            device.ping(gateway)


def test_devices(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Test device operations using DHCP emulation. """
    logger.info(test_devices.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('dhcp_sample.tcc').as_posix())
    reserve_ports(stc, locations, wait_for_up=True)

    # Retrieve DHCP servers and clients from configuration file.
    for port in stc.project.ports.values():
        for emulated_device in port.devices.values():
            emulated_device.get_children()
    dhcp_clients = stc.project.ports['Port 1'].get_objects_with_object('emulateddevice', 'ipv4if')
    dhcp_server_device = stc.project.ports['Port 2'].get_object_by_name('DHCP Server')
    dhcp_server = dhcp_server_device.get_child('dhcpv4serverconfig')

    # Start server and clients by starting the devices.
    dhcp_server_device.start()
    assert dhcp_server.get_attribute('ServerState') == 'UP'
    for dhcp_client_device in dhcp_clients:
        dhcp_client_device.start(wait_after=16)
        dhcp_client = dhcp_client_device.get_child('dhcpv4blockconfig')
        assert dhcp_client.get_attribute('BlockState') == 'BOUND'

    # Stop server by stopping the server itself.
    dhcp_server.command('Dhcpv4StopServer')
    assert dhcp_server.get_attribute('ServerState') == 'NONE'
    for dhcp_client_device in dhcp_clients:
        dhcp_client_device.stop()
        dhcp_client = dhcp_client_device.get_child('dhcpv4blockconfig')
        assert dhcp_client.get_attribute('BlockState') == 'IDLE'

    stc.start_devices()
    assert dhcp_server.get_attribute('ServerState') == 'UP'

    stc.stop_devices()
    assert dhcp_server.get_attribute('ServerState') == 'NONE'

    dhcp_server_device.command_emulations('Dhcpv4StartServer')
    assert dhcp_server.get_attribute('ServerState') == 'UP'

    # Test get_emulations and start_emulations.
    dhcp_clients = stc.project.get_emulations('dhcpv4blockconfig')
    stc.project.start_emulations(dhcp_clients, wait_after=8)
    for dhcp_client in dhcp_clients:
        assert dhcp_client.get_attribute('BlockState') == 'BOUND'


def test_port_traffic(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Test traffic and counters. """
    logger.info(test_port_traffic.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('test_config.xml').as_posix())
    reserve_ports(stc, locations, wait_for_up=True)

    gen_stats = StcStats('GeneratorPortResults')
    analyzer_stats = StcStats('analyzerportresults')

    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0
    assert analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0
    assert (gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
            analyzer_stats.get_counter('Port 2', 'SigFrameCount'))

    stc.project.ports['Port 1'].start()
    stc.project.ports['Port 1'].stop()
    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert (gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
            analyzer_stats.get_counter('Port 2', 'SigFrameCount'))

    stc.project.ports['Port 1'].clear_results()
    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0
    assert analyzer_stats.get_counter('Port 2', 'SigFrameCount') != 0
    stc.project.ports['Port 2'].clear_results()
    analyzer_stats.read_stats()
    assert analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0

    stc.start_traffic(blocking=True)
    stc.stop_traffic()
    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert (gen_stats.get_counter('Port 2', 'GeneratorFrameCount') ==
            analyzer_stats.get_counter('Port 1', 'SigFrameCount'))

    stc.clear_results()
    gen_stats.read_stats('GeneratorFrameCount')
    analyzer_stats.read_stats('SigFrameCount')
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0
    assert analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0


def test_sequencer(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Test Sequencer commands. """
    logger.info(test_sequencer.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('test_sequencer.tcc').as_posix())
    reserve_ports(stc, locations, wait_for_up=True)

    stc.sequencer_command(StcSequencerOperation.start)
    stc.sequencer_command(StcSequencerOperation.wait)

    gen_stats = StcStats('GeneratorPortResults')
    analyzer_stats = StcStats('analyzerportresults')

    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') >= 7900


def test_custom_view(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Test custom statistics view.

    Need to create proper configuration.
    """
    logger.info(test_custom_view.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('test_custom_views.tcc').as_posix())
    reserve_ports(stc, locations, wait_for_up=True)

    stc.project.ports['Port 1'].start(blocking=True)

    user_stats = StcStats('UserDynamicResultView')
    gen_stats = StcStats('GeneratorPortResults')

    gen_stats.read_stats()
    print(gen_stats.statistics)

    user_stats.read_stats()
    print(user_stats.statistics)
    print(user_stats.get_stats('Port.GeneratorFrameCount'))
    print(user_stats.get_object_stats('Port 1', obj_id_stat='Port.Name'))
    print(user_stats.get_stat('Port 1', 'Port.GeneratorFrameCount', obj_id_stat='Port.Name'))

    gen_stats = StcStats('GeneratorPortResults')
    analyzer_stats = StcStats('analyzerportresults')

    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0
    assert analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0
    assert (gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
            analyzer_stats.get_counter('Port 2', 'SigFrameCount'))

    stc.project.ports['Port 1'].start()
    stc.project.ports['Port 1'].stop()
    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert (gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
            analyzer_stats.get_counter('Port 2', 'SigFrameCount'))


def test_single_port_traffic(logger: logging.Logger, stc: StcApp, locations: List[str]) -> None:
    """ Test traffic and counters in loopback mode.

    This test cannot run on virtual ports.
    """
    logger.info(test_single_port_traffic.__doc__.strip())

    stc.load_config(Path(__file__).parent.joinpath('configs').joinpath('loopback.tcc').as_posix())
    reserve_ports(stc, locations[0:1], wait_for_up=True)

    gen_stats = StcStats('generatorportresults')
    analyzer_stats = StcStats('analyzerportresults')

    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0
    assert analyzer_stats.get_counter('Port 1', 'SigFrameCount') == 0
    assert (gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
            analyzer_stats.get_counter('Port 1', 'SigFrameCount'))

    stc.project.ports['Port 1'].start()
    stc.project.ports['Port 1'].stop()
    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') != 0
    assert analyzer_stats.get_counter('Port 1', 'SigFrameCount') != 0
    assert (gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
            analyzer_stats.get_counter('Port 1', 'SigFrameCount'))

    stc.project.ports['Port 1'].clear_results()
    gen_stats.read_stats()
    analyzer_stats.read_stats()
    assert gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0
    assert analyzer_stats.get_counter('Port 1', 'SigFrameCount') == 0


def reserve_ports(stc: StcApp, locations: List[str], wait_for_up: bool = True) -> None:
    """ Reserver ports.

    :param stc: STC server.
    :param locations: Ports locations as chassis/card/port.
    :param wait_for_up: True - wait for ports to come up (timeout after 80 seconds), False - return immediately.
    """
    ports = stc.project.ports.values()
    for port, location in list(zip(ports, locations)):
        port.reserve(location, force=False, wait_for_up=False)
    if wait_for_up:
        for port in ports:
            port.wait_for_states(40, 'UP')