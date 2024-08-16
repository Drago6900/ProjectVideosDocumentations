import asyncio
import json
import websockets
import paho.mqtt.client as mqtt

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect to MQTT broker")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Disconnected from MQTT broker")

# Function to publish MQTT message
def publish_mqtt(client, name, number):
    # Publish message
    client.publish("PersonData", json.dumps({"Name": name, "CardID": number}))
    data = json.dumps({"Name": name, "CardID": number})
    print("Published MQTT message:", data)
    print("Success")

# Main function
async def main():
    # MQTT client setup
    mqtt_username = "mqttuser"
    mqtt_password = "Mosbach74821"
    mqtt_client = mqtt.Client(client_id="nametag")  # Specify MQTT client ID
    mqtt_client.username_pw_set(mqtt_username, mqtt_password)  # Set MQTT username and password
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.connect("MIP-10741P.mpdv.cloud", 30101, 120)  # Establish MQTT connection
    mqtt_client.loop_start()  # Start the MQTT client loop
    
    # You can add your custom logic here to publish MQTT messages or perform other actions
    # For example:
    publish_mqtt(mqtt_client, "John", "123456")
    
    # Keep the program running indefinitely
    await asyncio.Future()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())