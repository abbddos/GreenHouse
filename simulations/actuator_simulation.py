import paho.mqtt.client as mqtt
import json 
import requests 

mqtt_client = mqtt.Client(client_id="FlaskAPI") 

TOPIC_READINGS = "greenhouse/1/readings" 


def receive_latest_status(greenhouse_id):
    API_URL_LATEST = f"http://127.0.0.1:5002/api/v1/actuator_status/{greenhouse_id}/latest"
    try:
        response = requests.get(API_URL_LATEST)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest data from API: {e}")
        return {}
    
    except KeyError as e:
        print(f"Error parsing data from API: Missing key {e}")
        return None
    
    
def send_data(data, greenhouse_id):
    API_URL = f"http://127.0.0.1:5002/api/v1/actuator_status/{greenhouse_id}"
    try:
        response = requests.post(API_URL, json = data)
        response.raise_for_status()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest data from API: {e}")

    


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC_READINGS)

    else:
        print(f"Failed to connect, return code {rc}\n")
        
        
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed to topic: {TOPIC_READINGS} with QoS: {granted_qos}")
    
    
def on_message(client, userdata, msg):
    
    """Callback for when a PUBLISH message is received from the broker."""
    print(f"Received message on topic '{msg.topic}': {msg.payload.decode()}")
    
    latest_status = receive_latest_status(1)
    
        
    # You can use if to handle different topics with different logic
    if "readings" in msg.topic:
        print("This is a sensor reading message.")
        try:
            data = json.loads(msg.payload.decode('utf-8'))
            
            if "timestamp" in latest_status.keys():
                del latest_status["timestamp"]
                
            if "id" in latest_status.keys():
                del latest_status["id"]
                            
            if data != latest_status:
                send_data(data, 1)
                
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from readings: {e}")
        
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
