"""
Base class for all STC package tests.

@author yoram@ignissoft.com
"""

from os import path

from trafficgenerator.test.test_tgn import TgnTest

from testcenter.api.stc_tcl import StcTclWrapper
from testcenter.api.stc_python import StcPythonWrapper
from testcenter.api.stc_rest import StcRestWrapper
from testcenter.stc_app import StcApp

stc_config_files = ('configs/test_config.tcc',
                    'configs/dhcp_sample.tcc',
                    'configs/statistics.tcc',
                    'configs/ospf_sample.tcc',
                    'configs/analyzer_sample.tcc',
                    'configs/loopback.tcc')


class StcTestBase(TgnTest):

    stc = None

    TgnTest.config_file = path.join(path.dirname(__file__), 'TestCenter.ini')

    def setUp(self):
        super(StcTestBase, self).setUp()
        if self.config.get('STC', 'api').lower() == 'tcl':
            api_wrapper = StcTclWrapper(self.logger, self.config.get('STC', 'install_dir'))
        elif self.config.get('STC', 'api').lower() == 'python':
            api_wrapper = StcPythonWrapper(self.logger, self.config.get('STC', 'install_dir'))
        else:
            api_wrapper = StcRestWrapper(self.logger, self.config.get('STC', 'lab_server'))
        self.stc = StcApp(self.logger, api_wrapper=api_wrapper)
        log_level = self.config.get('STC', 'log_level')
        self.stc.system.get_child('automationoptions').set_attributes(LogLevel=log_level)
        self.stc.connect()

    def tearDown(self):
        super(StcTestBase, self).tearDown()
        self.stc.disconnect()

    def testHelloWorld(self):
        pass
