import paho.mqtt.client as mqtt
import json 

mqtt_client = mqtt.Client(client_id="FlaskAPI") 
TOPIC = "greenhouse/1/heater"

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}\n")
        
        
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed to topic: {TOPIC} with QoS: {granted_qos}")
    
    
def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the broker."""
    print(f"Received message on topic '{msg.topic}': {msg.payload.decode()}")
    
    # You can use if/elif to handle different topics with different logic
    if "readings" in msg.topic:
        print("This is a sensor reading message.")
        try:
            # Assuming readings are JSON, you can parse them
            data = json.loads(msg.payload.decode('utf-8'))
            print(f"Parsed reading data: {data}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from readings: {e}")
            
    elif "heater" in msg.topic:
        print("This is a heater command message.")
        try:
            # Assuming heater commands are JSON
            data = json.loads(msg.payload.decode('utf-8'))
            print(f"Parsed heater command: {data['command']}")
            # You could add logic here to turn a physical heater on/off
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from heater command: {e}")
    else:
        print("Received a message on an unexpected topic.")
        
mqtt_client.on_connect = on_connect
mqtt_client.on_subscribe = on_subscribe
mqtt_client.on_message = on_message
mqtt_client.connect("localhost", 1883, 60)

try:
    mqtt_client.loop_forever()

except KeyboardInterrupt:
    print("Exiting...")

finally:
    mqtt_client.disconnect()
