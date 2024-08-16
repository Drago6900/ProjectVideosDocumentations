import socket

def wake_on_lan(mac_address, ip_address, port=9):
    mac_bytes = bytearray.fromhex(mac_address.replace(':', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(magic_packet, (ip_address, port))

# Example usage
targets = [
    ('80:00:0B:44:8E:69', '192.168.0.101'),
    ('80:00:0B:27:14:06', '192.168.0.100') # mac & IP addresses of the targeted computers
]

for mac, ip in targets:
    wake_on_lan(mac, ip) 