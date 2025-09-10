import socket
import subprocess
import platform

def ping_sweep(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return [f"Host {host} is up"]
        else:
            return [f"Host {host} is down"]
    except Exception as e:
        return [f"Ping error: {str(e)}"]

def tcp_ping(host, port=80):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            return [f"Host {host} responded to TCP ping on port {port}"]
        else:
            return [f"No response from {host} on TCP port {port}"]
    except Exception as e:
        return [f"TCP ping error: {str(e)}"]
    finally:
        sock.close()