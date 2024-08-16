import asyncio
import json
import websockets
import requests
import time
import subprocess
import re
import socket


def get_ip_address():
    hostname = socket.gethostname()
    own_ip_address = socket.gethostbyname(hostname)
    return own_ip_address

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
mac_address = "20-7B-D2-22-EF-E3"  # Replace with the MAC address of the device

# Retrieve the IP address associated with the MAC address
ip_address = get_ip_from_mac(mac_address)

async def handler(websocket):
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        reply = {"accessRecordId": data['accessRecordId']}
        print(reply)
        name = {"name": "username"}
        await websocket.send(json.dumps(reply))
        
        if 'accessRecordId' in data:
           
            entity = data.get('entity', {})
            score = entity.get('score')
            names = entity.get('personInfo', {}).get('name')
            number = entity.get('personInfo', {}).get('no')
            if score and float(score) > 0.8:
                r = requests.get(f"http://{ip_address}:5000/open-file", params={'number': number})
                print('middle pc', r.text)  # displays the result body.
                print("success")
                time.sleep(10)
            else:
                print('Invalid user, please try again.')

async def main():
    own_ip_address = get_ip_address()
    async with websockets.serve(handler, own_ip_address, 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())