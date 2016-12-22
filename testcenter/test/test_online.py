"""
TestCenter package tests that require actual TestCenter chassis and active ports.

These tests serve two purposes:
- Unit test for TestCenter package.
- Code snippet showing how to work with TestCenter package.

Test setup:
Two STC ports connected back to back.

@author yoram@ignissoft.com
"""

from os import path

from testcenter.stc_statistics_view import StcStats
from testcenter.stc_port import MediaType

from testcenter.test.test_base import stc_config_files
from testcenter.test.test_offline import StcTestOffline


class StcTestOnline(StcTestOffline):

    media_type = MediaType.fiber

    ports = []

    def testReservePorts(self):
        """ Load configuration and reserve ports. """
        self.testLoadConfig()
        project = self.stc.project
        self.ports = project.get_children('port')
        project.get_object_by_name('Port 1').reserve(self.config.get('STC', 'port1'))
        project.get_object_by_name('Port 2').reserve(self.config.get('STC', 'port2'))
        for port in self.ports:
            port.set_media_type(self.media_type)
        pass

    def testOnline(self):
        """ Load configuration on ports and verify that ports are online. """
        self.testReservePorts()
        for port in self.ports:
            assert(port.is_online())
        pass

    def testArp(self):
        """ Test ARP commands. """
        self.testReservePorts()
        self.stc.send_arp_ns()
        for port in self.ports:
            port.send_arp_ns()
            for device in port.get_children('emulateddevice'):
                device.send_arp_ns()
            for sb in port.get_children('streamblock'):
                sb.send_arp_ns()
        pass

    # If this test fails, consider adding delay between ping commands.
    def testPing(self):
        self.testReservePorts()
        self.stc.send_arp_ns()
        for port in self.ports:
            for device in port.get_children('emulateddevice'):
                gateway = device.get_child('ipv4if', 'ipv6if').get_attribute('Gateway')
                device.ping(gateway)
        pass

    def testDevices(self):
        """ Test device operations using DHCP emulation. """

        self.stc_config_file = path.join(path.dirname(__file__), stc_config_files[1])
        self.testReservePorts()

        # Retrieve DHCP servers and clients from configuration file.
        self.ports[0].get_subtree(types=['emulateddevice'], level=2)
        self.ports[1].get_subtree(types=['emulateddevice'], level=2)
        dhcp_clients = self.ports[0].get_objects_with_object('emulateddevice', 'ipv4if')
        dhcp_server_device = self.ports[1].get_object_by_name('DHCP Server')
        dhcp_server = dhcp_server_device.get_child('dhcpv4serverconfig')

        # Start server and clients by starting the devices.
        dhcp_server_device.start()
        assert(dhcp_server.get_attribute('ServerState') == 'UP')
        for dhcp_client_device in dhcp_clients:
            dhcp_client_device.start(wait_after=8)
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
        self.stc.project.start_emulations(dhcp_clients)
        for dhcp_client in dhcp_clients:
            assert(dhcp_client.get_attribute('BlockState') == 'BOUND')

        pass

    def testPortTraffic(self):

        self.testReservePorts()
        self.stc.send_arp_ns()

        gen_stats = StcStats('generatorportresults')
        analyzer_stats = StcStats('analyzerportresults')

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

        self.stc.start_traffic()
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

        pass

    def testStats(self):

        self.stc_config_file = path.join(path.dirname(__file__), stc_config_files[0])
        self.testReservePorts()

        self.stc.start_traffic(blocking=False)

        gen_stats = StcStats('generatorportresults')
        analayzer_stats = StcStats('analyzerportresults')
        sb_tx_stats = StcStats('txstreamblockresults')
        sb_rx_stats = StcStats('rxstreamblockresults')
        fg_tx_stats = StcStats('txstreamresults')
        fg_rx_stats = StcStats('rxstreamsummaryresults')

        gen_stats.read_stats()
        analayzer_stats.read_stats()
        sb_tx_stats.read_stats()
        sb_rx_stats.read_stats()
        fg_tx_stats.read_stats()
        fg_rx_stats.read_stats()

        p1_gen_counters = gen_stats.get_object_stats('Port 1')
        print p1_gen_counters['GeneratorFrameCount']
        print analayzer_stats.get_counter('Port 2', 'SigFrameCount')

    def testSinglePortTraffic(self):

        self.stc_config_file = path.join(path.dirname(__file__), 'configs/loopback.tcc')
        self.testLoadConfig()
        self.ports = self.stc.project.get_children('port')
        self.stc.project.get_object_by_name('Port 1').reserve(self.config.get('STC', 'port1'))

        gen_stats = StcStats('generatorportresults')
        analyzer_stats = StcStats('analyzerportresults')

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

    def testLoadChassis(self):
        resources = []
        self.stc.connect(chassis='10.224.18.200')
        chassis_manager = self.stc.system.get_child('PhysicalChassisManager')
        chassis = chassis_manager.get_child('PhysicalChassis')
        resources.append(chassis)
        for test_module in chassis.get_children('PhysicalTestModule'):
            description = test_module.get_attribute('Description')
            if description:
                resources.append(test_module)
                for port_group in test_module.get_children('PhysicalPortGroup'):
                    resources.append(port_group)
                    for port in port_group.get_children('PhysicalPort'):
                        resources.append(port)
        print ', '.join(r.obj_ref() for r in resources)
