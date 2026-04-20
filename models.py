from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = "Admin"
    admin_ID = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

class Doctor(db.Model):
    __tablename__ = "Doctor"
    doctor_ID = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    specialisation = db.Column(db.String, nullable=False)
    availability = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    contact = db.Column(db.Integer, nullable=False)

class Patient(db.Model):
    __tablename__ = "Patient"
    patient_ID = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)
    login = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)

class Department(db.Model):
    __tablename__ = "Department"
    department_ID = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

class Appointment(db.Model):
    __tablename__ = "Appointment"
    appointment_ID = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    patient_ID = db.Column(db.Integer, nullable=False)
    doctor_ID = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)


class Treatment(db.Model):
    __tablename__ = "Treatment"
    appointment_ID = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    diagnosis = db.Column(db.String)
    prescription = db.Column(db.String)
    notes = db.Column(db.String)
    symptoms = db.Column(db.String)

class Blacklist(db.Model):
    __tablename__ = "Blacklist"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String, nullable=False)
