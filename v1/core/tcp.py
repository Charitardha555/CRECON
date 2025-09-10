import socket
import concurrent.futures

def scan_port(host, port, callback=None, progress_callback=None):
    if progress_callback:
        progress_callback(port)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        if result == 0:
            if callback:
                callback(f"[+] Open TCP port: {port}")
            return port
    except:
        pass
    finally:
        sock.close()
    return None

def tcp_full_connect_scan(host, ports, callback=None, progress_callback=None):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(scan_port, host, port, callback, progress_callback): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:
                open_ports.append(result)
    return open_ports  # Still return full list (for banner grabbing etc.)

def syn_scan(host, ports, callback=None, progress_callback=None):
    # SYN scan using scapy (requires root/admin)
    from scapy.all import IP, TCP, sr1, conf
    conf.verb = 0
    open_ports = []
    for port in ports:
        if progress_callback:
            progress_callback(port)
        pkt = IP(dst=host)/TCP(dport=port, flags='S')
        resp = sr1(pkt, timeout=0.5, verbose=0)
        if resp is not None and resp.haslayer(TCP):
            if resp[TCP].flags == 0x12:  # SYN-ACK
                open_ports.append(port)
                if callback:
                    callback(f"[+] Open TCP port (SYN): {port}")
                # Send RST to close connection
                rst_pkt = IP(dst=host)/TCP(dport=port, flags='R')
                sr1(rst_pkt, timeout=0.2, verbose=0)
    return open_ports
