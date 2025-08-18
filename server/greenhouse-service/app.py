from flask import Flask, jsonify 
from flask_cors import CORS 
from models import Greenhouse, Readings, ActuatorStatus
from database import db, init_db 
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})

@app.route('/')
def index():
    return jsonify({"message": "It works!!!"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port= 5002, debug = True)