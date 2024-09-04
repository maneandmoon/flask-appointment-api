from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
import string, datetime

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)
db = SQLAlchemy(metadata=metadata)


class Patient(db.Model, SerializerMixin):
    __tablename__ = "patient_table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    patient_appointments = db.relationship('Appointment', back_populates='patient_list')
    doctors = association_proxy('patient_appointments', 'doctor_list')

    serialize_rules = ('-patient_appointments.doctor_list',)

    def __repr__(self):
        return f'<Patient {self.id} {self.name} >'



class Appointment(db.Model, SerializerMixin):
    __tablename__ = "appointment_table"
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String, nullable=False)

    # created_at = db.Column(db.DateTime, server_default=db.func.now())
    # updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_table.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_table.id'))

    doctor_list = db.relationship('Doctor', back_populates='doctor_appointments')
    patient_list = db.relationship('Patient', back_populates='patient_appointments')

    doctor = association_proxy('doctor_list', 'doctor_name')
    patient = association_proxy('patient_list', 'patient_name')

    serialize_rules = ('-doctor_list.doctor_appointments', '-patient_list.patient_appointments')

    @validates('day')
    def validate_day(self, key, day):
        if day not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            raise ValueError("Appointment day must be between Monday and Friday")
        return day

    def __repr__(self):
        return f'<Appointment {self.id} {self.day} >'



class Doctor(db.Model, SerializerMixin):
    __tablename__ = "doctor_table"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    specialty = db.Column(db.String, nullable=False)

    doctor_appointments = db.relationship('Appointment', back_populates='doctor_list')
    patients = association_proxy('doctor_appointments', 'patient_list')

    serialize_rules = ('-doctor_appointments.doctor_list',)

    @validates('name')
    def validate_name(self, key, name):
        if not name.startswith('Dr.'):
            raise ValueError("Doctor's name must start with 'Dr.'")
        return name


    def __repr__(self):
        return f'<Doctor {self.id} {self.name} {self.specialty} >'