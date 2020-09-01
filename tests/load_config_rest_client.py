import getpass
from pathlib import Path
from random import randint

from stcrestclient import stchttp


server = 'localhost'
port = 8888
session_name = 'session' + str(randint(0, 99))
user_name = getpass.getuser()
config_file = Path('configs/test_config.xml')

stc_http = stchttp.StcHttp(server, port, debug_print=True)
stc_session = stc_http.new_session(user_name, session_name, kill_existing=True)

stc_http.upload(config_file.as_posix())
stc_http.perform('LoadFromXml', {'FileName': config_file.name})

stc_http.perform('ResetConfig', {'config': 'system1'})
stc_http.end_session(end_tcsession=True)
