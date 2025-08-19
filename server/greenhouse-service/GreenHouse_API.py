from flask import Blueprint, jsonify, request 
from models import Greenhouse
from database import db 

greenhouse_bp = Blueprint('greenhouse_bp', __name__, url_prefix='/api/v1/greenhouse')


@greenhouse_bp.route('/', methods = ['POST'])
def create_greenhouse():
    try:
         data = request.get_json()
         if not data:
             return jsonify({"error": "No data provided"}), 400
         
         new_greenhouse = Greenhouse(
             name = data.get('name'),
             location = data.get('location'),
             target_temp = data.get('target_temp'),
             target_humidity = data.get('target_humidity'),
             target_soil_moisture_pct =  data.get('target_soil_moisture_pct'),
             target_light = data.get('target_light'),
             target_co_two = data.get('target_CO2'),
             target_wind_speed = data.get('target_wind_speed')
         )
         
         db.session.add(new_greenhouse)
         db.session.commit() 
         return jsonify(new_greenhouse.serialize()), 201
     
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500 
    
    
@greenhouse_bp.route('/', methods = ['GET'])
def get_all_greenhouses():
    try:
        all_greenhouses = Greenhouse.query.all() 
        greenhouse_list = [greenhouse.serialize() for greenhouse in all_greenhouses]
        return jsonify(greenhouse_list), 200
    
    except Exception as e:
        return jsonify({"error":str(e)}), 500
    
    
@greenhouse_bp.route('/<int:greenhouse_id>', methods = ['GET'])
def get_greenhouses(greenhouse_id):
    greenhouse = Greenhouse.query.get(greenhouse_id)
    if not greenhouse:
        return jsonify({"error":"Greenhouse not found"}), 404
    
    return jsonify(greenhouse.serialize()), 200


@greenhouse_bp.route('/<int:greenhouse_id>', methods = ['PUT'])
def update_greenhouse(greenhouse_id):
    try:
        greenhouse = Greenhouse.query.get(greenhouse_id)
        if not greenhouse:
            return jsonify({"error":"Greenhouse not found"}), 404
    
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        greenhouse.name = data.get('name', greenhouse.name)
        greenhouse.location = data.get('location', greenhouse.location)
        greenhouse.target_temp = data.get('target_temp', greenhouse.target_temp)
        greenhouse.target_humidity = data.get('target_humidity', greenhouse.target_humidity)
        greenhouse.target_soil_moisture_pct = data.get('target_soil_moisture_pct', greenhouse.target_soil_moisture_pct)
        greenhouse.target_light = data.get('target_light', greenhouse.target_light)
        greenhouse.target_co_two = data.get('target_co_two', greenhouse.target_co_two)
        greenhouse.target_wind_speed = data.get('target_wind_speed', greenhouse.target_wind_speed)
        
        db.session.commit()
        return jsonify(greenhouse.serialize()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    
@greenhouse_bp.route('/<int:greenhouse_id>', methods = ['DELETE'])
def delete_greenhouse(greenhouse_id):
    try:
        greenhouse = Greenhouse.query.get(greenhouse_id) 
        if not greenhouse:
            return jsonify({"error": "Greenhouse not found"}), 404 
        
        db.session.delete(greenhouse)
        db.session.commit() 
        return jsonify({"message": "Greenhouse deleted successfully"}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


    
    
    
    