import platform
import socket

def passive_os_detection():
    try:
        os_name = platform.system()
        os_version = platform.version()
        return [f"Operating System: {os_name} {os_version}"]
    except Exception as e:
        return [f"OS detection error: {str(e)}"]

import subprocess

def detect_ttl_os(host):
    try:
        proc = subprocess.run(['ping', '-c', '1', host], capture_output=True, text=True)
        output = proc.stdout

        for line in output.splitlines():
            if "ttl=" in line.lower():
                ttl_value = int(line.split("ttl=")[1].split()[0])
                if ttl_value <= 64:
                    return ["Likely Linux/Unix"]
                elif ttl_value <= 128:
                    return ["Likely Windows"]
                elif ttl_value <= 255:
                    return ["Likely Cisco/Unix"]
                else:
                    return [f"Unknown TTL Value: {ttl_value}"]
        return ["TTL not found in ping reply."]
    except Exception as e:
        return [f"Error: {e}"]
