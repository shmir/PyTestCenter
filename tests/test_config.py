"""
Tests configuration file.
"""
CHASSIS_511 = "10.254.30.14"
SERVER_511 = "localhost:9090"

server_properties = {
    "windows_511": {
        "server": SERVER_511,
        "locations": [f"{CHASSIS_511}/1/1", f"{CHASSIS_511}/1/4"],
        "install_dir": "C:/Program Files/Spirent Communications/Spirent TestCenter 5.11",
    }
}

# Default for options.
api = ["rest"]
server = ["windows_511"]
