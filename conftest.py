
def pytest_addoption(parser):
    parser.addoption(
        "--api", action="store", default="rest", help="api option: tcl, python or rest"
    )
