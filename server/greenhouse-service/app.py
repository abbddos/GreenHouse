from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from config import Config
from database import db, init_db 
import paho.mqtt.client as mqtt 
from datetime import datetime
import os 
import threading 

app = Flask(__name__)

app.config.from_object(Config)

init_db(app)

CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})

mqtt_client = mqtt.Client(client_id="FlaskAPI") 

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")

from GreenHouse_API import greenhouse_bp
from Readings_API import readings_bp


app.register_blueprint(greenhouse_bp, url_prefix='/api/v1/greenhouse')
app.register_blueprint(readings_bp, url_prefix='/api/v1/readings')



@app.route('/')
def index():
    return jsonify({"message":"it fucking works!!!"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    try:
        # Use a public test broker. You should use a local broker or a cloud service for production.
        broker_address = "localhost"
        port = 1883
        mqtt_client.connect(broker_address, port=port, keepalive=60)
        # Start a background thread to handle MQTT network traffic.
        mqtt_client.loop_start()
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
 
        
    app.run(port = 5002, debug = True)
    