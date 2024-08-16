import subprocess
import re

def get_ip_from_mac(mac_address):
    # Run the arp -a command to get ARP table
    arp_output = subprocess.run(["arp", "-a"], capture_output=True, text=True)

    # Parse ARP table to find the IP address associated with the MAC address
    arp_lines = arp_output.stdout.splitlines()
    for line in arp_lines:
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", line)
        if match:
            ip = match.group(1)
            mac = match.group(0).split()[1]
            if mac.lower() == mac_address.lower():
                return ip
    return None

# Specify the MAC address of the device
mac_address = "00-14-38-a6-c5-e8"  # Replace with the MAC address of the device

# Retrieve the IP address associated with the MAC address
ip_address = get_ip_from_mac(mac_address)
if ip_address:
    print(f"The IP address associated with MAC address {mac_address} is: {ip_address}")
else:
    print(f"Could not find the IP address associated with MAC address {mac_address}")