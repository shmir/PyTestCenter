
chassis_505 = '192.168.65.35'
server_505 = 'localhost:8888'

server_properties = {'windows_505': {'server': server_505,
                                     'locations': [f'{chassis_505}/1/1', f'{chassis_505}/1/2'],
                                     'install_dir': 'C:/Program Files/Spirent Communications/Spirent TestCenter 5.05'}}

# Default for options.
api = ['rest']
server = ['windows_505']
