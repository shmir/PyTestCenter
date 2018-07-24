"""
Base class for all STC package tests.

@author yoram@ignissoft.com
"""

from os import path
import logging
import pytest

from trafficgenerator.tgn_utils import ApiType
from trafficgenerator.test.test_tgn import TgnTest

from testcenter.stc_app import init_stc


class StcTestBase(TgnTest):

    stc = None

    TgnTest.config_file = path.join(path.dirname(__file__), 'TestCenter.ini')

    def setUp(self):

        # To support non pytest runners.
        try:
            self.api = ApiType[pytest.config.getoption('--api')]  # @UndefinedVariable
        except Exception as _:
            self.api = ApiType[TgnTest.config.get('Server', 'api')]

        logging.basicConfig(level=self.config.get('Logging', 'level'))
        logging.getLogger().addHandler(logging.FileHandler(self.config.get('Logging', 'file_name')))
        super(StcTestBase, self).setUp()
        self.stc = init_stc(self.api, self.logger, self.config.get('STC', 'install_dir'),
                            self.config.get('Server', 'rest_server'), self.config.get('Server', 'rest_port'))
        log_level = self.config.get('STC', 'log_level')
        self.stc.system.get_child('automationoptions').set_attributes(LogLevel=log_level)
        ls = None if self.config.get('Server', 'lab_server') == 'None' else self.config.get('Server', 'lab_server')
        self.stc.connect(ls)

    def tearDown(self):
        super(StcTestBase, self).tearDown()
        self.stc.disconnect()

    def testHelloWorld(self):
        pass
