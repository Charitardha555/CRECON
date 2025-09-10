import socket
import logging

# Logging setup
def setup_logger():
    logging.basicConfig(
        filename='crecon.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_ports(port_range):
    ports = set()
    if '-' in port_range:
        start, end = port_range.split('-')
        ports.update(range(int(start), int(end) + 1))
    elif ',' in port_range:
        for port in port_range.split(','):
            ports.add(int(port.strip()))
    else:
        ports.add(int(port_range.strip()))
    return sorted(list(ports))

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False
