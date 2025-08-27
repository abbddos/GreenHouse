from flask import Blueprint, jsonify, request, current_app 
from models import Greenhouse, Readings
from database import db 

readings_bp = Blueprint('readings_bp', __name__, url_prefix='/api/v1/readings')


def mqtt_messaging(greenhouse_id, reading):
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
    
    # Temperature Control
    if reading.temp_celsius > greenhouse.target_temp + temp_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/heater", '{"command": "OFF"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/vents", '{"command":"ON}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/humidifier", '{"command": "ON"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "ON"}')
    elif reading.temp_celsius < greenhouse.target_temp - temp_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/heater", '{"command": "ON"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/vents", '{"command": "OFF"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/humidifier", '{"command": "OFF"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "OFF"}')
       
    # Humidity Control 
    if reading.humidity_pct < greenhouse.target_humidity - humidity_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/humidifier", '{"command": "ON"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "OFF"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/vents", '{"command": "OFF"}')
    elif reading.humidity_pct > greenhouse.target_humidity + humidity_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/humidifier", '{"command": "OFF"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "ON"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/vents", '{"command": "ON"}')
        
    # Soil Moisture Control
    if reading.soil_moisture_pct < greenhouse.target_soil_moisture_pct - soil_moisture_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/irrigation", '{"command": "ON"}')
    elif reading.soil_moisture_pct > greenhouse.target_soil_moisture_pct + soil_moisture_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/irrigation", '{"command": "OFF"}')
        
    # Light Control
    if reading.light_lux < greenhouse.target_light - light_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/lights", '{"command": "ON"}')
    elif reading.light_lux > greenhouse.target_light + light_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/lights", '{"command": "OFF"}')
        
    # CO2 Control
    if reading.co_two > greenhouse.target_co_two + co2_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/vents", '{"command": "ON"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "ON"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/lights", '{"command": "OFF"}')
    elif reading.co_two < greenhouse.target_co_two - co2_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/vents", '{"command": "OFF"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "OFF"}')
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/lights", '{"command": "ON"}')
        
    # Wind Speed Control
    if reading.wind_speed > greenhouse.target_wind_speed + wind_speed_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "ON"}')
    elif reading.wind_speed < greenhouse.target_wind_speed - wind_speed_margin:
        current_app.mqtt_client.publish(f"greenhouse/{greenhouse_id}/fan", '{"command": "OFF"}')



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
        all_readings_list = [reading.serialize for reading in all_readings]
        return jsonify(all_readings_list), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
    
    
@readings_bp.route('/<int:greenhouse_id>/latest', methods = ['GET'])
def get_latest_reading(greenhouse_id):
    try:
        latest_reading = Readings.query.filter_by(greenhouse_id = greenhouse_id).order_by(Readings.timestamp.desc()).first()
        return jsonify(latest_reading.serialize()), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

