"""
Tests for ixexplorer package.
"""
from pathlib import Path
from typing import List

from trafficgenerator import ApiType, TgnSutUtils, set_logger

from testcenter.stc_app import StcApp, init_stc


class StcSutUtils(TgnSutUtils):
    """STC SUT utilities."""

    def stc(self, api: ApiType) -> StcApp:
        install_dir = self.sut.get("install_dir")
        stc = init_stc(api, install_dir, self.sut["server"]["ip"], self.sut["server"]["port"])
        lab_server = self.sut.get("lab_server")
        stc.connect(lab_server)
        return stc

    def locations(self) -> List[str]:
        chassis = self.sut["chassis"]["ip"]
        return [f"{chassis}/{port}" for port in self.sut["chassis"]["ports"]]


set_logger()
