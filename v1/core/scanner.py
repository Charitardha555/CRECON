from core.tcp import tcp_full_connect_scan, syn_scan
from core.udp import udp_scan
from core.banner import grab_banner
from core.discovery import ping_sweep, tcp_ping
from core.os_detect import passive_os_detection, detect_ttl_os
from core.utils import parse_ports

def scan_target(host, scan_type, port_range="1-1024", callback=None, progress_callback=None):
    results = []

    def send(line):
        if callback:
            callback(line)

    if scan_type == "ping scan":
        for line in ping_sweep(host):
            send(line)
        results.append("Ping scan completed.")

    elif scan_type == "tcp ping":
        for line in tcp_ping(host):
            send(line)
        results.append("TCP ping completed.")

    elif scan_type == "tcp connect":
        ports = parse_ports(port_range)
        open_ports = tcp_full_connect_scan(host, ports, callback=send, progress_callback=progress_callback)
        banners_to_show = []
        if open_ports:
            results.append("Open TCP Ports:")
            send("Open TCP Ports:")
            for port in open_ports:
                line = f"  - [+] Open TCP port: {port}"
                send(line)
            # Only show banners with actual content or error (not empty)
            banner_info = grab_banner(host, open_ports)
            for b in banner_info:
                if b.strip():
                    banners_to_show.append(b)
            if banners_to_show:
                results.append("\nService Banners:")
                send("\nService Banners:")
                for b in banners_to_show:
                    line = f"  - {b}"
                    send(line)
                    results.append(line)
        else:
            results.append("No open TCP ports found.")
            send("No open TCP ports found.")

    elif scan_type == "syn scan":
        ports = parse_ports(port_range)
        open_ports = syn_scan(host, ports, callback=send, progress_callback=progress_callback)
        if open_ports:
            results.append("Open TCP Ports (SYN):")
            send("Open TCP Ports (SYN):")
            for port in open_ports:
                line = f"  - [+] Open TCP port (SYN): {port}"
                send(line)
        else:
            results.append("No open TCP ports found (SYN scan).")
            send("No open TCP ports found (SYN scan).")

    elif scan_type == "udp scan":
        ports = parse_ports(port_range)
        open_ports = udp_scan(host, ports)
        if open_ports:
            results.append("Open or Filtered UDP Ports:")
            send("Open or Filtered UDP Ports:")
            for port in open_ports:
                line = f"  - Open/Filtered UDP port: {port}"
                send(line)
        else:
            results.append("No open/filtered UDP ports found.")
            send("No open/filtered UDP ports found.")

    elif scan_type == "os detect":
        results.append("Passive OS Fingerprinting:")
        send("Passive OS Fingerprinting:")
        for line in passive_os_detection():
            send(line)
        results.append("\nTTL-Based OS Detection:")
        send("\nTTL-Based OS Detection:")
        for line in detect_ttl_os(host):
            send(line)

    else:
        results.append("Invalid scan type selected.")
        send("Invalid scan type selected.")

    return results
