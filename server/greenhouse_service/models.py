from database import db 
import datetime 

class Greenhouse(db.Model):
    __tablename__ = 'greenhouse'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    location = db.Column(db.String(100), nullable = False)
    target_temp = db.Column(db.Float, default = 25.0)
    target_humidity = db.Column(db.Float, default = 60.0)
    target_soil_moisture_pct = db.Column(db.Float, default = 40.0)
    target_light = db.Column(db.Float, default = 500.0)
    target_co_two = db.Column(db.Float, default = 400.0)
    target_wind_speed = db.Column(db.Float, default = 1.0)
    
    readings = db.relationship('Readings', backref = 'greenhouse', lazy = True,  cascade="all, delete-orphan")
    actuator_status = db.relationship('ActuatorStatus', backref = 'greenhouse', lazy = True,  cascade="all, delete-orphan")
    
    
    def __init__(self, name, location, target_temp, target_humidity, target_soil_moisture_pct, target_light, target_co_two, target_wind_speed):
        self.name = name 
        self.location = location 
        self.target_temp = target_temp
        self.target_humidity = target_humidity
        self.target_soil_moisture_pct = target_soil_moisture_pct
        self.target_light = target_light
        self.target_co_two = target_co_two
        self.target_wind_speed = target_wind_speed
        
        
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'target_temp': self.target_temp,
            'target_humidity': self.target_humidity,
            'target_soil_moisture_pct': self.target_soil_moisture_pct,
            'target_light': self.target_light,
            'target_CO2': self.target_co_two, 
            'target_wind_speed': self.target_wind_speed,
            'Readings': [reading.serialize() for reading in self.readings],
            'Actuator Statuses': [status.serialize() for status in self.actuator_status]
        }
        
        
    
    def __repr__(self):
        return f'<Greenhouse {self.name}>'
    
    
    
class Readings(db.Model):
    __tablename__ = 'readings'
    
    id = db.Column(db.Integer, primary_key = True)
    greenhouse_id = db.Column(db.Integer, db.ForeignKey('greenhouse.id'), nullable = False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    temp_celsius = db.Column(db.Float, nullable = True)
    humidity_pct = db.Column(db.Float, nullable = True)
    soil_moisture_pct = db.Column(db.Float, nullable = True)
    light_lux = db.Column(db.Float, nullable = True)
    co_two = db.Column(db.Float, nullable = True)
    wind_speed = db.Column(db.Float, nullable = True)
    
    def __init__(self, greenhouse_id, temp_celsius, humidity_pct, soil_moisture_pct, light_lux, co_two, wind_speed):
        self.greenhouse_id = greenhouse_id
        self.temp_celsius = temp_celsius
        self.humidity_pct = humidity_pct
        self.soil_moisture_pct = soil_moisture_pct
        self.light_lux = light_lux
        self.co_two = co_two
        self.wind_speed = wind_speed
        
        
    def serialize(self):
        return {
            'id': self.id,
            'greenhouse id': self.greenhouse_id,
            'timestamp': self.timestamp,
            'temp_celsius': self.temp_celsius,
            'humidity_pct': self.humidity_pct,
            'soil_moisture_pct': self.soil_moisture_pct,
            'light_lux': self.light_lux,
            'CO2': self.co_two,
            'wind speed': self.wind_speed
        }
    
    
    def __repr__(self):
        return f'<Reading {self.id}>'
    
    
class ActuatorStatus(db.Model):
    __tablename__ = 'actuator_status'
    
    id = db.Column(db.Integer, primary_key = True)
    greenhouse_id = db.Column(db.Integer, db.ForeignKey('greenhouse.id'), nullable = False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    vents_on = db.Column(db.Boolean, nullable = False, default = False)
    fan_on = db.Column(db.Boolean, nullable = False, default = False)
    lights_on = db.Column(db.Boolean, nullable = False, default = False)
    curtains_on = db.Column(db.Boolean, nullable = False, default = False)
    irrigation_pump_on = db.Column(db.Boolean, nullable = False, default = False)
    humidifier_pump_on = db.Column(db.Boolean, nullable = False, default = False)
    heater_on = db.Column(db.Boolean, nullable = False, default = False)
    
    def __init__(self, greenhouse_id, vents, fan, light, curtains, irrigation_pump, humidifier, heater):
        self.greenhouse_id = greenhouse_id
        self.vents_on = vents 
        self.fan_on = fan 
        self.lights_on = light 
        self.curtains_on = curtains 
        self.irrigation_pump_on = irrigation_pump
        self.humidifier_pump_on = humidifier 
        self.heater_on = heater
        
        
    def serialize(self):
        return {
            'id': self.id,
            'greenhouse id': self.greenhouse_id,
            'timestamp': self.timestamp,
            'vents on': self.vents_on,
            'fan on': self.fan_on,
            'lights on': self.lights_on,
            'curtains on': self.curtains_on,
            'irrigation pump on': self.irrigation_pump_on,
            'humidifier pump on': self.humidifier_pump_on,
            'heater on': self.heater_on
        }
    
    def __repr__(self):
        return f'<ActuatorStatus {self.id}>'
    
    