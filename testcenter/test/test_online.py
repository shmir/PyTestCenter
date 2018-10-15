"""
TestCenter package tests that require actual TestCenter chassis and active ports.

Test setup:
Two STC ports connected back to back.

@author yoram@ignissoft.com
"""

from os import path

from testcenter.stc_statistics_view import StcStats
from testcenter.stc_app import StcSequencerOperation

from testcenter.test.test_base import TestStcBase


class TestStcOnline(TestStcBase):

    ports = []

    def test_online(self):
        """ Load configuration on ports and verify that ports are online. """
        self.logger.info(TestStcOnline.test_online.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        self._reserve_ports()

        for port in self.ports:
            assert(port.is_online())

        for port in self.ports:
            port.release()

        self.stc.project.get_object_by_name('Port 1').reserve(wait_for_up=False)
        self.stc.project.get_object_by_name('Port 2').reserve(wait_for_up=False)

        pass

    def test_arp(self):
        """ Test ARP commands. """
        self.logger.info(TestStcOnline.test_arp.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        self._reserve_ports()

        self.stc.send_arp_ns()
        for port in self.ports:
            port.send_arp_ns()
            for device in port.get_children('emulateddevice'):
                device.send_arp_ns()
            for sb in port.get_children('streamblock'):
                sb.send_arp_ns()

    # If this test fails, consider adding delay between ping commands.
    def test_ping(self):
        """ Test Ping commands. """
        self.logger.info(TestStcOnline.test_ping.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        self._reserve_ports()

        self.stc.send_arp_ns()
        for port in self.ports:
            for device in port.get_children('emulateddevice'):
                gateway = device.get_child('ipv4if', 'ipv6if').get_attribute('Gateway')
                device.ping(gateway)

    def test_devices(self):
        """ Test device operations using DHCP emulation. """
        self.logger.info(TestStcOnline.test_devices.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/dhcp_sample.tcc'))

        self._reserve_ports()

        # Retrieve DHCP servers and clients from configuration file.
        for port in self.ports:
            for emulateddevice in port.get_children_by_type('emulateddevice'):
                emulateddevice.get_children()
        dhcp_clients = self.ports[0].get_objects_with_object('emulateddevice', 'ipv4if')
        dhcp_server_device = self.ports[1].get_object_by_name('DHCP Server')
        dhcp_server = dhcp_server_device.get_child('dhcpv4serverconfig')

        # Start server and clients by starting the devices.
        dhcp_server_device.start()
        assert(dhcp_server.get_attribute('ServerState') == 'UP')
        for dhcp_client_device in dhcp_clients:
            dhcp_client_device.start(wait_after=16)
            dhcp_client = dhcp_client_device.get_child('dhcpv4blockconfig')
            assert(dhcp_client.get_attribute('BlockState') == 'BOUND')

        # Stop server by stopping the server itself.
        dhcp_server.command('Dhcpv4StopServer')
        assert(dhcp_server.get_attribute('ServerState') == 'NONE')
        for dhcp_client_device in dhcp_clients:
            dhcp_client_device.stop()
            dhcp_client = dhcp_client_device.get_child('dhcpv4blockconfig')
            assert(dhcp_client.get_attribute('BlockState') == 'IDLE')

        self.stc.start_devices()
        assert(dhcp_server.get_attribute('ServerState') == 'UP')

        self.stc.stop_devices()
        assert(dhcp_server.get_attribute('ServerState') == 'NONE')

        dhcp_server_device.command_emulations('Dhcpv4StartServer')
        assert(dhcp_server.get_attribute('ServerState') == 'UP')

        # Test get_emulations and start_emulations.
        dhcp_clients = self.stc.project.get_emulations('dhcpv4blockconfig')
        self.stc.project.start_emulations(dhcp_clients, wait_after=8)
        for dhcp_client in dhcp_clients:
            assert(dhcp_client.get_attribute('BlockState') == 'BOUND')

    def test_port_traffic(self):
        """ Test traffic and counters. """
        self.logger.info(TestStcOnline.test_port_traffic.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        self._reserve_ports()

        gen_stats = StcStats(self.stc.project, 'GeneratorPortResults')
        analyzer_stats = StcStats(self.stc.project, 'analyzerportresults')

        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0)
        assert(analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0)
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
               analyzer_stats.get_counter('Port 2', 'SigFrameCount'))

        self.ports[0].start()
        self.ports[0].stop()
        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
               analyzer_stats.get_counter('Port 2', 'SigFrameCount'))

        self.ports[0].clear_results()
        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0)
        assert(analyzer_stats.get_counter('Port 2', 'SigFrameCount') != 0)
        self.ports[1].clear_results()
        analyzer_stats.read_stats()
        assert(analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0)

        self.stc.start_traffic(blocking=True)
        self.stc.stop_traffic()
        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 2', 'GeneratorFrameCount') ==
               analyzer_stats.get_counter('Port 1', 'SigFrameCount'))

        self.stc.clear_results()
        gen_stats.read_stats('GeneratorFrameCount')
        analyzer_stats.read_stats('SigFrameCount')
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0)
        assert(analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0)

    def test_sequencer(self):
        """ Test Sequencer commands. """
        self.logger.info(TestStcOnline.test_sequencer.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_sequencer.tcc'))
        self._reserve_ports()

        self.stc.sequencer_command(StcSequencerOperation.start)
        self.stc.sequencer_command(StcSequencerOperation.wait)

        gen_stats = StcStats(self.stc.project, 'GeneratorPortResults')
        analyzer_stats = StcStats(self.stc.project, 'analyzerportresults')

        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 8000)

    def test_custom_view(self):
        """ Test custom statistics view. """
        self.logger.info(TestStcOnline.test_custom_view.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        self._reserve_ports()
        self.ports[0].start(blocking=True)

        user_stats = StcStats(self.stc.project, 'UserDynamicResultView')
        gen_stats = StcStats(self.stc.project, 'GeneratorPortResults')

        gen_stats.read_stats()
        print(gen_stats.statistics)

        user_stats.read_stats()
        print(user_stats.statistics)
        print(user_stats.get_stats('Port.GeneratorFrameCount'))
        print(user_stats.get_object_stats('Port 1', obj_id_stat='Port.Name'))
        print(user_stats.get_stat('Port 1', 'Port.GeneratorFrameCount', obj_id_stat='Port.Name'))

#         gen_stats = StcStats(self.stc.project, 'GeneratorPortResults')
#         analyzer_stats = StcStats(self.stc.project, 'analyzerportresults')
#
#         gen_stats.read_stats()
#         analyzer_stats.read_stats()
#         assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0)
#         assert(analyzer_stats.get_counter('Port 2', 'SigFrameCount') == 0)
#         assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
#                analyzer_stats.get_counter('Port 2', 'SigFrameCount'))
#
#         self.ports[0].start()
#         self.ports[0].stop()
#         gen_stats.read_stats()
#         analyzer_stats.read_stats()
#         assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
#                analyzer_stats.get_counter('Port 2', 'SigFrameCount'))

    def test_single_port_traffic(self):
        """ Test traffic and counters in loopback mode. """
        self.logger.info(TestStcOnline.test_single_port_traffic.__doc__.strip())

        self.stc_config_file = path.join(path.dirname(__file__), 'configs/loopback.tcc')
        self.stc.load_config(self.stc_config_file)
        self.ports = self.stc.project.get_children('port')
        self.stc.project.get_object_by_name('Port 1').reserve(self.config.get('STC', 'port1'))

        gen_stats = StcStats(self.stc.project, 'generatorportresults')
        analyzer_stats = StcStats(self.stc.project, 'analyzerportresults')

        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0)
        assert(analyzer_stats.get_counter('Port 1', 'SigFrameCount') == 0)
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
               analyzer_stats.get_counter('Port 1', 'SigFrameCount'))

        self.ports[0].start()
        self.ports[0].stop()
        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') != 0)
        assert(analyzer_stats.get_counter('Port 1', 'SigFrameCount') != 0)
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') ==
               analyzer_stats.get_counter('Port 1', 'SigFrameCount'))

        self.ports[0].clear_results()
        gen_stats.read_stats()
        analyzer_stats.read_stats()
        assert(gen_stats.get_counter('Port 1', 'GeneratorFrameCount') == 0)
        assert(analyzer_stats.get_counter('Port 1', 'SigFrameCount') == 0)

    def _reserve_ports(self):
        project = self.stc.project
        self.ports = project.get_children('port')
        project.get_object_by_name('Port 1').reserve(self.config.get('STC', 'port1'), force=True, wait_for_up=False)
        project.get_object_by_name('Port 2').reserve(self.config.get('STC', 'port2'), force=True, wait_for_up=False)
        for port in self.ports:
            port.wait_for_states(40, 'UP')
