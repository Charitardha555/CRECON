import socket
import random

def udp_scan(host, ports):
    open_or_filtered_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1.0)
            message = bytes([random.randint(0, 255) for _ in range(4)])
            sock.sendto(message, (host, port))
            try:
                data, _ = sock.recvfrom(1024)
                open_or_filtered_ports.append(port)  # Received data: port probably open
            except socket.timeout:
                open_or_filtered_ports.append(port)  # No response: port open|filtered
        except Exception:
            continue
        finally:
            sock.close()
    return open_or_filtered_ports  # Return just raw port numbers (integers)
