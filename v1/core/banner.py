import socket

def grab_banner(host, ports):
    results = []
    for port in ports:
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((host, port))
            banner = ""
            # Try protocol-specific requests for common ports
            if port == 80:  # HTTP
                sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            elif port == 443:  # HTTPS (encrypted, skip)
                results.append(f"[Port {port}] Banner: Cannot grab banner for encrypted service (HTTPS)")
                sock.close()
                continue
            elif port == 25:  # SMTP
                pass
            elif port == 21:  # FTP
                pass
            elif port == 110:  # POP3
                pass
            elif port == 143:  # IMAP
                pass
            # Add more protocols as needed
            try:
                banner = sock.recv(1024).decode(errors="replace").strip()
            except Exception:
                banner = ""
            if banner:
                # Only show the first line for clarity
                first_line = banner.splitlines()[0] if banner.splitlines() else banner
                results.append(f"[Port {port}] Banner: {first_line}")
            # Do not append 'No banner returned' to keep output clean
        except Exception as e:
            results.append(f"[Port {port}] Error grabbing banner: {str(e)}")
        finally:
            sock.close()
    return results
