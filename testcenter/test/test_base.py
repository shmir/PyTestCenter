"""
Base class for all STC package tests.

@author yoram@ignissoft.com
"""

from os import path

from trafficgenerator.tgn_utils import ApiType
from trafficgenerator.test.test_tgn import TgnTest

from testcenter.stc_app import init_stc


class StcTestBase(TgnTest):

    stc = None

    TgnTest.config_file = path.join(path.dirname(__file__), 'TestCenter.ini')

    def setUp(self):
        super(StcTestBase, self).setUp()
        self.stc = init_stc(ApiType[self.config.get('STC', 'api')], self.logger, self.config.get('STC', 'install_dir'),
                            self.config.get('STC', 'lab_server'))
        log_level = self.config.get('STC', 'log_level')
        self.stc.system.get_child('automationoptions').set_attributes(LogLevel=log_level)
        self.stc.connect()

    def tearDown(self):
        super(StcTestBase, self).tearDown()
        self.stc.disconnect()

    def testHelloWorld(self):
        pass
