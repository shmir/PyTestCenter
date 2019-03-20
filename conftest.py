
import pytest

from trafficgenerator.tgn_utils import ApiType


def pytest_addoption(parser):
    parser.addoption('--api', action='store', default="tcl", help="api options: rest, tcl or python")
    parser.addoption('--server', action='store', default="localhost", help="REST server in format ip:port")
    parser.addoption('--ls', action='store', default=None, help="lab server address")
    parser.addoption('--port1', action='store', default="10.212.8.8/11/5", help="chassis1/module1/port1")
    parser.addoption('--port2', action='store', default="10.212.8.8/11/6", help="chassis2/module2/port2")


@pytest.fixture(scope='class', autouse=True)
def api(request):
    request.cls.api = ApiType[request.param]
    server_ip = request.config.getoption('--server')  # @UndefinedVariable
    request.cls.server_ip = server_ip.split(':')[0]
    request.cls.server_port = server_ip.split(':')[1] if len(server_ip.split(':')) == 2 else 8888
    request.cls.ls = request.config.getoption('--ls')
    request.cls.port1 = request.config.getoption('--port1')
    request.cls.port2 = request.config.getoption('--port2')


def pytest_generate_tests(metafunc):
    if metafunc.config.getoption('--api') == 'all':
        apis = ['tcl', 'rest']
    else:
        apis = [metafunc.config.getoption('--api')]
    metafunc.parametrize('api', apis, indirect=True)
