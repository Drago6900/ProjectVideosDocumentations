import asyncio
import json
import websockets
import requests
import time
from switch import turn_on_switch
from mes import login
from wakepc import wake_on_lan

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
                    point = data.get('entity')
                    point2 = point.get('score')
                    user_id = data.get('entity').get('userId', 'unknown')
                    print("Extracted score:", point2)
                    
                    if float(point2) < 0.8:
                        print('Invalid user, please try again.')
                    else:
                        # Wake up PCs first
                        wake_on_lan('80:00:0B:27:14:06', '192.168.0.100')
                        wake_on_lan('80:00:0B:44:8E:69', '192.168.0.101')
                        wake_on_lan('00:1A:2B:3C:4D:5E', '192.168.0.103')
                        
                        # Then proceed with other actions
                        turn_on_switch()
                        login()
                        name = {"name": "username"}
                        r = requests.post("http://192.168.0.100:5000", data=name)
                        print('middle pc', r.text)
                        r = requests.post("http://192.168.0.101:5000", data=name)
                        print('right pc', r.text)
                        r = requests.post("http://192.168.0.103:5000", data=name)
                        
                        print("success")
            else:
                print("Received old syncTime, skipping this event.")
                
    except websockets.ConnectionClosed:
        print("WebSocket connection closed")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Connection closed")

async def main():
    print("Starting WebSocket server on ws://192.168.0.104:8000")
    async with websockets.serve(handler, "192.168.0.102", 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Failed to start server: {e}")



