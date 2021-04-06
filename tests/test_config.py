
chassis_511 = '192.168.65.24'
server_511 = '10.100.102.25:8888'

server_properties = {'windows_511': {'server': server_511,
                                     'locations': [f'{chassis_511}/1/1', f'{chassis_511}/1/2'],
                                     'install_dir': 'C:/Program Files/Spirent Communications/Spirent TestCenter 5.11'}}

# Default for options.
api = ['rest']
server = ['windows_511']
