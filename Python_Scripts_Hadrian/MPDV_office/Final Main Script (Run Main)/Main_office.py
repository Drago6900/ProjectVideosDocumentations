import asyncio
import json
import websockets
import time
import socket
import requests
from Compare_office import compare_and_sync

# Get the script start time in milliseconds
script_start_time = int(time.time() * 1000)

# Define sleep duration in seconds (24 hours = 86400 seconds)
SLEEP_DURATION = 86400 # For how often you would like FaceSec & HYDRA to sync 

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
                    if score and float(score) > 0.8: # condition can be changed so as the 'score'
                        r = requests.get(f"http://172.17.170.73:5000/open-file", params={'number': number}) # Change IP address to client's
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

def get_ip_address():
    hostname = socket.gethostname()
    own_ip_address = socket.gethostbyname(hostname)
    return own_ip_address

async def compare_and_sync_periodically():
    while True:
        compare_and_sync()
        await asyncio.sleep(SLEEP_DURATION)  # Wait for 24 hours (86400 seconds)

async def main():
    own_ip_address = get_ip_address()
    websocket_server = websockets.serve(handler, own_ip_address, 8000)
    
    await asyncio.gather(
        websocket_server,
        compare_and_sync_periodically()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to start server: {e}")