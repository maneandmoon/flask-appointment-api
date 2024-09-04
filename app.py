#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime 
from models import db, Doctor, Patient, Appointment
from flask_restful import Resource, Api

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

api = Api(app)

db.init_app(app)


# | HTTP Verb 	|       Path       	| Description        	|
# |-----------	|:----------------:	|--------------------	|
# | GET       	|       /doctors  	| READ all resources 	|
# | GET       	|   /doctors/:id 	| READ one resource   	|/doctors/<int:id>
# | POST      	|       /doctors   	| CREATE one resource 	|
# | PATCH/PUT 	| /patients/:id 	| UPDATE one resource	|
# | DELETE    	|/appointments/:id 	| DESTROY one resource 	|

#   - GET /doctors
#   - GET /doctors/<int:id>
#   - POST /doctors
#   - GET /patients/<int:id>
#   - PATCH /patients/<int:id>
#   - POST /appointments
#   - DELETE /appointments/<int:id>

@app.get("/")
def index():
    return "doctor/patient"

class DoctorResource(Resource):
    def get(self, id=None):
        if id:
            doctor = Doctor.query.filter_by(id=id).first()
            # doctor = Doctor.query.get(id)
            if doctor:
                return doctor.to_dict(), 200
            if not doctor:  
                return {"message": "Doctor {id} not found"}, 404
        doctors = Doctor.query.all()
        doctor_dict = [doctor.to_dict() for doctor in doctors]
        return make_response(doctor_dict, 200)

        # return [doctor.to_dict() for doctor in doctors], 200

    def post(self):
        data = request.get_json()
        try:
            # new_doctor = Doctor(name=data['name'], specialty=data['specialty'])
            new_doctor = Doctor(name=data.get('name'), specialty=data.get('specialty'))

            db.session.add(new_doctor)
            db.session.commit()
            return make_response(new_doctor.to_dict(), 200)
        except:
            return make_response({'message': 'something went wrong '}, 422)
        
api.add_resource(DoctorResource, '/doctors', '/doctors/<int:id>')

class PatientResource(Resource):
    def get(self, id):
        patient = Patient.query.get(id)
        if patient:
            return patient.to_dict(), 200
        return make_response({"message": "Patient not found"}, 404)

    def patch(self, id):
        data = request.get_json()
        patient = Patient.query.get(id)
        if patient:
            if 'name' in data:
                patient.name = data.get('name')
            db.session.commit()
            return make_response(patient.to_dict(), 200)
        return make_response({"message": "Patient not found"}, 404)
    
api.add_resource(PatientResource, '/patients/<int:id>')

class AppointmentResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_appointment = Appointment(
                day=data['day'],
                doctor_id=data['doctor_id'],
                patient_id=data['patient_id']
            )
            db.session.add(new_appointment)
            db.session.commit()
            return new_appointment.to_dict(), 201
        except Exception as e:
            return {"message": str(e)}, 422

    def delete(self, id):
        appointment = Appointment.query.get(id)
        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            return {"message": "Appointment deleted"}, 204
        return make_response({"message": "Appointment not found"}, 404)

api.add_resource(AppointmentResource, '/appointments', '/appointments/<int:id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
