"""
Base class for all STC package tests.

@author yoram@ignissoft.com
"""

from os import path
import logging

from testcenter.stc_app import init_stc


class TestStcBase:

    stc = None

    def setup(self):

        super(TestStcBase, self).setup()

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
