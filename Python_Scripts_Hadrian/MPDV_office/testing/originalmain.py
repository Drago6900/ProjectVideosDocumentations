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
# mac_address = "08-26-AE-37-FE-03"  # Replace with the MAC address of the device

# Retrieve the IP address associated with the MAC address
# ip_address = get_ip_from_mac(mac_address)

# Get the script start time in milliseconds
script_start_time = int(time.time() * 1000)

async def handler(websocket, path):
    print("New connection established")
    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            # Extract syncTime from the entity field
            sync_time = data.get('entity', {}).get('syncTime', 0)
            
            # Print both script_start_time and sync_time
            print("script_start_time:", script_start_time)
            print("Received syncTime:", sync_time)
            
            # Check if the syncTime is greater than the script_start_time
            if sync_time > script_start_time:
                print("Processing event with syncTime:", sync_time)
                
                reply = {"accessRecordId": data['accessRecordId']}
                await websocket.send(json.dumps(reply))
                
                if 'accessRecordId' in data:
                    entity = data.get('entity', {})
                    score = entity.get('score')
                    names = entity.get('personInfo', {}).get('name')
                    number = entity.get('personInfo', {}).get('no')
                    if score and float(score) > 0.8:
                        r = requests.get(f"http://172.17.171.57:5000/open-file", params={'number': number})
                        print('middle pc', r.text)  # displays the result body.
                        print("success")
                        time.sleep(10)
                    else:
                        print("Received old syncTime, skipping this event.")
                
    except websockets.ConnectionClosed:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Connection closed")

async def main():
    own_ip_address = get_ip_address()
    async with websockets.serve(handler, own_ip_address, 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to start server: {e}")
