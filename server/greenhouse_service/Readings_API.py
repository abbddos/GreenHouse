from flask import Blueprint, jsonify, request, current_app 
from models import Greenhouse, Readings
from database import db
import json 
import datetime

readings_bp = Blueprint('readings_bp', __name__, url_prefix='/api/v1/readings')


def mqtt_messaging(greenhouse_id, reading):
    
    from app import mqtt_client 
    
    temp_margin = 2.0  # Celsius
    humidity_margin = 5.0 # Percentage
    soil_moisture_margin = 5.0 # Percentage
    light_margin = 100.0 # Lux
    co2_margin = 50.0 # ppm
    wind_speed_margin = 0.5 # m/s
    
    
    greenhouse = Greenhouse.query.get(greenhouse_id)
    if not greenhouse:
        print(f"Greenhouse with ID {greenhouse_id} not found.")
        return 
    
    message = {
        "greenhouse_id": greenhouse_id,
        "vents_on": "OFF", 
        "fan_on": "OFF",
        "lights_on": "OFF",
        "curtains_on": "OFF",
        "irrigation_pump_on": "OFF",
        "humidifier_pump_on": "OFF",
        "heater_on": "OFF"
    }
    
    # Temperature Control
    if reading.temp_celsius > greenhouse.target_temp + temp_margin:
        message['heater_on'] = "OFF"
        message['vents_on'] = "ON"
        message['humidifier_pump_on'] = "ON"
        message['fan_on'] = "ON"
    elif reading.temp_celsius < greenhouse.target_temp - temp_margin:
        message['heater_on'] = "ON"
        message['vents_on'] = "OFF"
        message['humidifier_pump_on'] = "OFF"
        message['fan_on'] = "OFF"

    # Humidity Control 
    if reading.humidity_pct < greenhouse.target_humidity - humidity_margin:
        message['humidifier_pump_on'] = "ON"
        message['fan_on'] = "OFF"
        message['vents_on'] = "OFF"
    elif reading.humidity_pct > greenhouse.target_humidity + humidity_margin:
        message['humidifier_pump_on'] = "OFF"
        message['fan_on'] = "ON"
        message['vents_on'] = "ON"
        
    # Soil Moisture Control
    if reading.soil_moisture_pct < greenhouse.target_soil_moisture_pct - soil_moisture_margin:
        message['irrigation_pump_on'] = "ON"
    elif reading.soil_moisture_pct > greenhouse.target_soil_moisture_pct + soil_moisture_margin:
        message['irrigation_pump_on'] = "OFF"
        
    # Light Control
    if reading.light_lux < greenhouse.target_light - light_margin:
        message['lights_on'] = "ON"
    elif reading.light_lux > greenhouse.target_light + light_margin:
        message['lights_on'] = "OFF"
        
    # CO2 Control
    if reading.co_two > greenhouse.target_co_two + co2_margin:
        message['vents_on'] = "ON" 
        message['fan_on'] = "ON" 
        message['lights_on'] = "OFF"
    elif reading.co_two < greenhouse.target_co_two - co2_margin:
        message['vents_on'] = "OFF" 
        message['fan_on'] = "OFF"
        message['lights_on'] = "ON"
        
    # Wind Speed Control
    if reading.wind_speed > greenhouse.target_wind_speed + wind_speed_margin:
        message['fan_on'] = "ON"
    elif reading.wind_speed < greenhouse.target_wind_speed - wind_speed_margin:
        message['fan_on'] = "OFF"
        
    mqtt_client.publish(f"greenhouse/{greenhouse_id}/readings", json.dumps(message), retain=True)



@readings_bp.route('/<int:greenhouse_id>', methods = ['POST'])
def add_reading(greenhouse_id):
    try:
        data = request.get_json() 
        if not data:
            return jsonify({"error":"No data is provided"}), 400 
        
        new_reading = Readings(
            greenhouse_id = greenhouse_id,
            temp_celsius = data.get('temp_celsius'),
            humidity_pct=data.get('humidity_pct'),
            soil_moisture_pct=data.get('soil_moisture_pct'),
            light_lux=data.get('light_lux'),
            co_two=data.get('co_two'),
            wind_speed=data.get('wind_speed')
        )
        
        db.session.add(new_reading)
        mqtt_messaging(greenhouse_id, new_reading)
        db.session.commit()
        
        return jsonify({"message":"Reading added and processed successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)})
    
    
@readings_bp.route('/<int:greenhouse_id>/all', methods = ['GET'])
def get_all_readings(greenhouse_id):
    try:
        all_readings = Readings.query.filter_by(greenhouse_id = greenhouse_id).order_by(Readings.timestamp.desc()).all()
        all_readings_list = [reading.serialize() for reading in all_readings]
        return jsonify(all_readings_list), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
        pass
    
    
@readings_bp.route('/<int:greenhouse_id>/latest', methods = ['GET'])
def get_latest_reading(greenhouse_id):
    try:
        latest_reading = Readings.query.filter_by(greenhouse_id = greenhouse_id).order_by(Readings.timestamp.desc()).first()
        return jsonify(latest_reading.serialize()), 200
        
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

