from flask import Blueprint, jsonify, request
from models import ActuatorStatus
from database import db 

actuator_status_bp = Blueprint('actuator_status_bp', __name__, url_prefix = '/api/v1/actuator_status')

@actuator_status_bp.route('/<int:greenhouse_id>', methods = ['POST'])
def add_actuator_status(greenhouse_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error":"No data provided"}), 400 
        
        new_status = ActuatorStatus(
            greenhouse_id=greenhouse_id,
            vents=data.get('vents on'),
            fan=data.get('fan on'),
            light=data.get('lights on'),
            curtains=data.get('curtains on'),
            irrigation_pump=data.get('irrigation pump on'),
            humidifier=data.get('humidifier pump on'),
            heater=data.get('heater on')
        ) 
        
        db.session.add(new_status)
        db.session.commit()
        
        return jsonify(new_status.serialize()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    
@actuator_status_bp.route('/<int:greenhouse_id>/all', methods = ['GET'])
def get_all_actuator_statuses(greenhouse_id):
    try:
        all_statuses = ActuatorStatus.query.filter_by(greenhouse = greenhouse_id).order_by(ActuatorStatus.timestamp.desc()).all()
        status_list = [status.serialize for status in all_statuses]
        
        return jsonify(status_list), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@actuator_status_bp.route('/<int:greenhouse_id>/latest', methods = ['GET'])
def get_latest_status(greenhouse_id):
    try:
        latest_status = ActuatorStatus.query.filter_by(greenhouse_id = greenhouse_id).order_by(ActuatorStatus.timestamp.desc()).first()
        return jsonify(latest_status.serialize), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
