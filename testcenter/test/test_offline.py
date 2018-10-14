"""
TestCenter package tests that can run in offline mode.

@author yoram@ignissoft.com
"""

from os import path
import inspect
import pytest

from trafficgenerator.tgn_utils import ApiType

from testcenter.stc_object import StcObject
from testcenter.stc_port import StcPort
from testcenter.stc_device import StcDevice
from testcenter.stc_stream import StcStream

from testcenter.test.test_base import TestStcBase


class TestStcOffline(TestStcBase):

    def test_load_config(self):
        """ Load existing configuration. """
        self.logger.info(TestStcOffline.test_load_config.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        file_name, file_ext = path.splitext(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        self.stc.save_config(file_name + '-save' + file_ext)

        with pytest.raises(Exception):
            self.stc.load_config(path.join(path.dirname(__file__), 'tcc.invalid'))
        with pytest.raises(Exception):
            self.stc.load_config(path.join(path.dirname(__file__), 'invalid.tcc'))

    def test_reload_config(self):
        """ Reload existing configuration. """
        self.logger.info(TestStcOffline.test_reload_config.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        for port in self.stc.project.get_ports().values():
            print(port.get_name())
        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        for port in self.stc.project.get_ports().values():
            print(port.get_name())

    def test_analyze_config(self):
        """ Analyze existing configuration. """
        self.logger.info(TestStcOffline.test_analyze_config.__doc__.strip())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        project = self.stc.project

        project.get_children('port')
        port1_obj = project.get_object_by_name('Port 1')

        print('Port1 object reference = ', port1_obj.obj_ref())
        print('Port1 name = ', port1_obj.obj_name())
        print('Ports = ', project.get_objects_by_type('port'))
        print('Port 1 state = ', port1_obj.get_attribute('Location'))
        print('Port 1 attributes = ', port1_obj.get_attributes())
        print('Port 1 streamblocks = ', port1_obj.get_children('streamblock'))
        print('Port 2 streamblocks = ', port1_obj.get_children('streamblock'))

        stc_ports = project.get_children('port')
        assert(len(stc_ports) == 2)

        assert(len(stc_ports[0].get_children('emulateddevice')) == 1)
        assert(len(stc_ports[1].get_children('emulateddevice')) == 1)

        assert(len(self.stc.project.get_devices()) == 2)
        assert(len(self.stc.project.get_devices(stc_ports[0])) == 1)
        assert(len(self.stc.project.get_devices(stc_ports[1])) == 1)

        assert(len(self.stc.project.get_children('GroupCollection')) == 1)
        assert(len(self.stc.project.get_object_by_name('TG 1').get_children('TrafficGroup')) == 1)
        assert(len(self.stc.project.get_object_by_name('TG 1').get_object_by_name('SG 1').get_stream_blocks()) == 2)
        assert(len(self.stc.project.get_stream_blocks()) == 2)

    def test_children(self):
        """ Test specific get children methods. """
        self.logger.info(TestStcOffline.test_children.__doc__)

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        project = self.stc.project

        ports = project.get_ports()
        assert(len(ports) == 2)
        for port in ports.values():
            assert(len(port.get_devices()) == 1)
            assert(len(port.get_stream_blocks()) == 1)

    def test_build_config(self):
        """ Build simple config from scratch. """
        self.logger.info(TestStcOffline.test_build_config.__doc__.strip())

        for port_name in ('Port 1', 'Port 2'):
            self.logger.info('Create Port "%s"', port_name)
            stc_port = StcPort(name=port_name, parent=self.stc.project)

            for dev_name in (port_name + ' Device 1', port_name + ' Device 2'):
                self.logger.info('Build Device "%s"', dev_name)
                stc_dev = StcDevice(name=dev_name, parent=stc_port)
                stc_eth = StcObject(objType='EthIIIf', parent=stc_dev)
                stc_eth.set_attributes(SourceMac='00:11:22:33:44:55')
                stc_ip = StcObject(objType='Ipv4If', parent=stc_dev)
                stc_ip.set_attributes(Address='1.2.3.4', PrefixLength=16)

            for sb_name in (port_name + ' StreamBlock 1', port_name + ' StreamBlock 2'):
                self.logger.info('Build StreamBlock "%s"', sb_name)
                stc_sb = StcStream(name=sb_name, parent=stc_port)
                stc_eth = StcObject(objType='ethernet:ethernetii', parent=stc_sb)
                stc_eth.set_attributes(DstMac='00:10:20:30:40:50')

        stc_ports = self.stc.project.get_children('port')
        assert(len(stc_ports) == 2)
        for stc_port in stc_ports:
            assert(len(stc_port.get_children('generator')) == 1)
            assert(len(stc_port.get_children('generator', 'analyzer')) == 2)
            assert(len(stc_port.get_children('emulateddevice')) == 2)
            assert(len(stc_port.get_children('emulateddevice', 'generator', 'analyzer')) == 4)
        for stc_port in stc_ports:
            assert(len(stc_port.get_children('streamblock')) == 2)

        test_name = inspect.stack()[0][3]
        self.stc.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.tcc'))

    def test_stream_under_project(self):
        """ Build simple config with ports under project object. """
        self.logger.info(TestStcOffline.test_stream_under_project.__doc__.strip())

        for port_name in ('Port 1', 'Port 2'):
            self.logger.info('Create Port "%s"', port_name)
            stc_port = StcPort(name=port_name, parent=self.stc.project)

            for sb_name in (port_name + ' StreamBlock 1', port_name + ' StreamBlock 2'):
                self.logger.info('Build StreamBlock "%s"', sb_name)
                stc_sb = StcStream(name=sb_name, parent=stc_port)
                stc_eth = StcObject(objType='ethernet:ethernetii', parent=stc_sb)
                stc_eth.set_attributes(DstMac='00:10:20:30:40:50')

        test_name = inspect.stack()[0][3]
        self.stc.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.tcc'))

    def test_build_emulation(self):
        """ Build simple BGP configuration. """
        self.logger.info(TestStcOffline.test_build_emulation.__doc__.strip())

        stc_port = StcPort(name='Port 1', parent=self.stc.project)
        stc_dev = StcDevice(name='Device 1', parent=stc_port)
        stc_eth = StcObject(objType='EthIIIf', parent=stc_dev)
        stc_eth.set_attributes(SourceMac='00:11:22:33:44:55')
        stc_ip = StcObject(objType='Ipv4If', parent=stc_dev)
        stc_ip.set_attributes(Address='1.2.3.4', PrefixLength=16)
        StcObject(objType='BgpRouterConfig', parent=stc_dev)

        test_name = inspect.stack()[0][3]
        self.stc.save_config(path.join(path.dirname(__file__), 'configs', test_name + '.tcc'))

    def test_backdoor(self):

        if self.api != ApiType.rest:
            self.skipTest('Skip test - non rest API')

        print(self.stc.api.ls.get(self.stc.project.ref, 'children').split())
        print(self.stc.api.ls.get(self.stc.project.ref, 'children-port').split())

        self.stc.load_config(path.join(path.dirname(__file__), 'configs/test_config.tcc'))
        ports = self.stc.api.ls.get(self.stc.project.ref, 'children-port').split()

        print(self.stc.api.ls.get(ports[0]))
        print(self.stc.api.ls.get(ports[0], 'Name'))
        print(self.stc.api.ls.get(ports[0], 'Name', 'Active'))

        print(self.stc.api.ls.config(ports[0], Name='New Name', Active=False))
        print(self.stc.api.ls.get(ports[0], 'Name', 'Active'))
