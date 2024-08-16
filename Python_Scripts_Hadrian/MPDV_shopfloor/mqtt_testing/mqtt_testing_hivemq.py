import asyncio
import json
import websockets
import requests
import paho.mqtt.client as mqtt

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

def publish_mqtt(client, name, number):
    # Publish message
    client.publish("PersonData", json.dumps({"Name": name, "CardID": number}))
    data = json.dumps({"Name": name, "CardID": number})
    print(data)

async def main():
    mqtt_client = mqtt.Client(client_id="nametag")  # Specify MQTT client ID
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.connect("localhost", 1883, 120)  # Establish MQTT connection
    mqtt_client.loop_start()  # Start the MQTT client loop
    async with websockets.serve(lambda ws, path: handler(ws, mqtt_client), "192.168.0.104", 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())