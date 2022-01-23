"""
Standard pytest fixtures and hooks definition file.
"""
# pylint: disable=redefined-outer-name
import logging
from pathlib import Path
from typing import Iterable, List

import pytest
from _pytest.config.argparsing import Parser
from trafficgenerator.tgn_conftest import api, logger, pytest_generate_tests, server, server_properties, tgn_pytest_addoption
from trafficgenerator.tgn_utils import ApiType

from testcenter.stc_app import StcApp, init_stc


def pytest_addoption(parser: Parser) -> None:
    """Add options to allow the user to determine which APIs and servers to test."""
    tgn_pytest_addoption(parser, Path(__file__).parent.joinpath("test_config.py").as_posix())


@pytest.fixture()
def stc(logger: logging.Logger, api: ApiType, server_properties: dict) -> Iterable[StcApp]:
    """Yields connected STC object."""
    install_dir = server_properties["install_dir"]
    reset_server, rest_port = server_properties["server"].split(":")
    stc = init_stc(api, logger, install_dir, reset_server, rest_port)
    lab_server = server_properties.get("lab_server")
    stc.connect(lab_server)
    yield stc
    stc.disconnect()


@pytest.fixture(scope="session")
def locations(server_properties: dict) -> List[str]:
    """Yields ports locations."""
    return server_properties["locations"]
