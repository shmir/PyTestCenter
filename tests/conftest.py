"""
Standard pytest fixtures and hooks definition file.
"""
# pylint: disable=redefined-outer-name
from typing import Iterable, List

import pytest
from trafficgenerator import ApiType
from trafficgenerator.tgn_conftest import api, log_level, pytest_addoption, sut  # pylint: disable=unused-import

from testcenter.stc_app import StcApp
from tests import StcSutUtils


@pytest.fixture(scope="session")
def sut_utils(sut: dict) -> StcSutUtils:
    """Yield the sut dictionary from the sut file."""
    return StcSutUtils(sut)


@pytest.fixture
def stc(sut_utils: StcSutUtils, api: ApiType) -> Iterable[StcApp]:
    """Yield connected STC object."""
    _stc = sut_utils.stc(api)
    yield _stc
    _stc.disconnect()


@pytest.fixture
def locations(sut_utils: StcSutUtils) -> List[str]:
    """Yield ports locations."""
    return sut_utils.locations()
