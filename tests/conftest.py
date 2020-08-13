
import logging
from pathlib import Path

import pytest
from _pytest.config.argparsing import Parser

from trafficgenerator.tgn_utils import ApiType
from trafficgenerator.tgn_conftest import tgn_pytest_addoption, pytest_generate_tests, logger, api, server, server_properties
from testcenter.stc_app import init_stc


def pytest_addoption(parser: Parser) -> None:
    """ Add options to allow the user to determine which APIs and servers to test. """
    tgn_pytest_addoption(parser, Path(__file__).parent.joinpath('test_config.py').as_posix())


@pytest.fixture()
def stc(logger: logging.Logger, api: ApiType, server_properties: dict):
    """ Yields connected STC object. """
    install_dir = server_properties['install_dir']
    reset_server, rest_port = server_properties['server'].split(':')
    stc = init_stc(api, logger, install_dir, reset_server, rest_port)
    lab_server = server_properties.get('lab_server')
    stc.connect(lab_server)
    yield stc
    stc.disconnect()
