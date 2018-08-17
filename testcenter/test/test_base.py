"""
Base class for all STC package tests.

@author yoram@ignissoft.com
"""

from os import path
import logging
import pytest

from trafficgenerator.tgn_utils import ApiType
from trafficgenerator.test.test_tgn import TestTgnBase

from testcenter.stc_app import init_stc


class StcTestBase(TestTgnBase):

    stc = None

    TestTgnBase.config_file = path.join(path.dirname(__file__), 'TestCenter.ini')

    def setup(self):

        self.api = ApiType[pytest.config.getoption('--api')]  # @UndefinedVariable

        logging.basicConfig(level=self.config.get('Logging', 'level'))
        logging.getLogger().addHandler(logging.FileHandler(self.config.get('Logging', 'file_name')))
        super(StcTestBase, self).setUp()
        self.stc = init_stc(self.api, self.logger, self.config.get('STC', 'install_dir'),
                            self.config.get('Server', 'rest_server'), self.config.get('Server', 'rest_port'))
        log_level = self.config.get('STC', 'log_level')
        self.stc.system.get_child('automationoptions').set_attributes(LogLevel=log_level)
        ls = None if self.config.get('Server', 'lab_server') == 'None' else self.config.get('Server', 'lab_server')
        self.stc.connect(ls)

    def teardown(self):
        super(StcTestBase, self).tearDown()
        self.stc.disconnect()

    def test_hello_world(self):
        pass
