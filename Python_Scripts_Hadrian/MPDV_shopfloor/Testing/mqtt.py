import asyncio
import json
import websockets
import requests
import paho.mqtt.client as mqtt
import time

# Get the script start time in milliseconds
script_start_time = int(time.time() * 1000)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect to MQTT broker")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Disconnected from MQTT broker")

async def handler(websocket, mqtt_client):
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
            print("accessRecordID:", data.get("accessRecordId"))
            print(reply)
            name = {"name": "username"}
            await websocket.send(json.dumps(reply))
            
            if 'accessRecordId' in data:
                entity = data.get('entity', {})
                score = entity.get('score')
                names = entity.get('personInfo', {}).get('name')
                number = entity.get('personInfo', {}).get('no')
                if score and float(score) > 0.8:
                    print("success")
                    publish_mqtt(mqtt_client, names, number)  # Publish MQTT message
                else:
                    print('Invalid user, please try again.')
        else:
            print("Received old syncTime, skipping this event.")

def publish_mqtt(client, name, number):
    # Publish message
    client.publish("PersonData", json.dumps({"Name": name, "CardID": number}))
    data = json.dumps({"Name": name, "CardID": number})
    print(data)

async def main():
    mqtt_client = mqtt.Client(client_id="nametag")  # Specify MQTT client ID
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.username_pw_set(username="mqttuser", password="Mosbach74821")  # Set MQTT username and password
    mqtt_client.connect("MIP-10741P.mpdv.cloud", 30101, 120)  # Establish MQTT connection
    mqtt_client.loop_start()  # Start the MQTT client loop
    async with websockets.serve(lambda ws, path: handler(ws, mqtt_client), "172.17.171.69", 8000): #your ip address & port number used
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

