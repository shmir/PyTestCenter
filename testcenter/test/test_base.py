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


class TestStcBase(TestTgnBase):

    stc = None

    TestTgnBase.config_file = path.join(path.dirname(__file__), 'TestCenter.ini')

    def setup(self):

        super(TestStcBase, self).setup()
        self._get_config()

        logging.basicConfig(level=self.config.get('Logging', 'level'))
        logging.getLogger().addHandler(logging.FileHandler(self.config.get('Logging', 'file_name')))
        super(TestStcBase, self).setup()
        self.stc = init_stc(self.api, self.logger, self.config.get('STC', 'install_dir'), self.server_ip,
                            self.server_port)
        log_level = self.config.get('STC', 'log_level')
        self.stc.system.get_child('automationoptions').set_attributes(LogLevel=log_level)
        self.stc.connect(self.ls)

    def teardown(self):
        super(TestStcBase, self).teardown()
        self.stc.disconnect()

    def test_hello_world(self):
        pass

    def _get_config(self):

        self.api = ApiType[pytest.config.getoption('--api')]  # @UndefinedVariable
        server_ip = pytest.config.getoption('--server')  # @UndefinedVariable
        self.server_ip = server_ip.split(':')[0]
        self.server_port = server_ip.split(':')[1] if len(server_ip.split(':')) == 2 else 8888
        self.ls = pytest.config.getoption('--ls')  # @UndefinedVariable
