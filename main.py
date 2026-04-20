import os
from flask import Flask, render_template, request
from models import db, Admin, Doctor, Patient, Appointment, Treatment, Department, Blacklist

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
db.init_app(app)

@app.route("/", methods=['GET', 'POST'])
def login():
    return render_template('home.html')

# ================= ADMIN SECTION =================

@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    admn = Admin.query.filter_by(admin_ID=request.form['login_id'], password=request.form['password']).first()
    if admn:
        return render_template('admin_dashboard.html', doctors=Doctor.query.all(), patients=Patient.query.all(), appointments=Appointment.query.all())
    return render_template('admin_login.html', error="Invalid ID or password")

@app.route("/admin/dashboard", methods=['GET'])
def admin_dashboard():
    return render_template('admin_dashboard.html', doctors=Doctor.query.all(), patients=Patient.query.all(), appointments=Appointment.query.all())

@app.route("/admin/dashboard/add_doctor", methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'GET':
        return render_template('add_doctor.html', departments=Department.query.all())
    special = request.form['specialisation']
    if not Department.query.filter_by(name=special).first():
        db.session.add(Department(name=special))
    new_doctor = Doctor(name=request.form['name'], specialisation=special, contact=request.form['contact'], password=request.form['password'])
    db.session.add(new_doctor); db.session.commit()
    return render_template('add_doctor_success.html', doctorn=new_doctor.name)

@app.route("/admin/dashboard/<doctor_id>")
def admin_doctors(doctor_id):
    return render_template('admin_doctors.html', doctor=Doctor.query.filter_by(doctor_ID=doctor_id).first())

@app.route("/admin/delete/<doctor_id>")
def delete_doctor(doctor_id):
    doctor = Doctor.query.filter_by(doctor_ID=doctor_id).first()
    db.session.delete(doctor); db.session.commit()
    return render_template('doctor_delete_success.html', doctorn=doctor.name)

@app.route("/admin/update/<doctor_id>", methods=['GET', 'POST'])
def update_doctor(doctor_id):
    doctor = Doctor.query.filter_by(doctor_ID=doctor_id).first()
    if request.method == 'GET':
        return render_template('doctor_update.html', doctor=doctor, departments=Department.query.all())
    doctor.specialisation = request.form['specialisation']; doctor.contact = request.form['contact']; doctor.password = request.form['password']
    if not Department.query.filter_by(name=doctor.specialisation).first():
        db.session.add(Department(name=doctor.specialisation))
    db.session.commit()
    return render_template('doctor_update_success.html', name=doctor.name)

@app.route("/admin/blacklist/<doctor_id>")
def blacklist_doctor(doctor_id):
    doc = Doctor.query.filter_by(doctor_ID=doctor_id).first()
    db.session.add(Blacklist(name=doc.name)); db.session.commit()
    return render_template("doctor_blacklisted_success.html", name=doc.name)

@app.route("/admin/view/doctor/<int:doctor_id>")
def admin_view_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    appointments = Appointment.query.filter_by(doctor_ID=doctor_id).all()
    for a in appointments:
        patient = Patient.query.get(a.patient_ID)
        a.patient_name = patient.name if patient else "Unknown"
    return render_template("view_doctor.html", doctor=doctor, upcoming_appointments=[a for a in appointments if a.status == "Upcoming"], previous_appointments=[a for a in appointments if a.status in ["Completed", "Cancelled"]])

@app.route("/admin/view/blacklist")
def view_blacklisted():
    blacklisted = Blacklist.query.all()
    for b in blacklisted:
        doc = Doctor.query.filter_by(name=b.name).first()
        b.doctor_ID = doc.doctor_ID if doc else "Unknown"
    return render_template("blacklisted_doctors.html", blacklisted=blacklisted)

@app.route("/admin/unblacklist/<int:doctor_id>")
def unblacklist_doctor(doctor_id):
    doc = Doctor.query.get(doctor_id)
    blk = Blacklist.query.filter_by(name=doc.name).first()
    db.session.delete(blk)
    db.session.commit()
    return render_template("admin_dashboard.html")

@app.route("/admin/view/patient/<int:patient_id>")
def admin_view_patient(patient_id):
    patient = Patient.query.get(patient_id)
    appointments = Appointment.query.filter_by(patient_ID=patient_id).all()
    for a in appointments:
        doc = Doctor.query.get(a.doctor_ID)
        a.doctor_name = doc.name if doc else "Unknown"
    return render_template("view_patient.html", patient=patient, upcoming_appointments=[a for a in appointments if a.status == "Upcoming"], previous_appointments=[a for a in appointments if a.status in ["Completed", "Cancelled"]])

# ================= DOCTOR SECTION =================

@app.route("/doctor/login", methods=['GET','POST'])
def doctor_login():
    if request.method == 'GET':
        return render_template('doctor_login.html')
    doc = Doctor.query.filter_by(doctor_ID=request.form['login_id'], password=request.form['password']).first()
    if not doc:
        return render_template('doctor_login.html', error="Invalid ID or password")
    appointments = Appointment.query.filter_by(doctor_ID=doc.doctor_ID).all()
    for a in appointments:
        patient = Patient.query.get(a.patient_ID)
        a.patient_name = patient.name if patient else "Unknown"
    return render_template('doctor_dashboard.html', doctorn=doc.name, doctor=doc, appointments=appointments)

@app.route("/doctor/dashboard/<doctor_id>", methods=['GET','POST'])
def doctor_dashboard(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if request.method == 'POST':
        doctor.availability = request.form['days']; db.session.commit()
    appointments = Appointment.query.filter_by(doctor_ID=doctor_id).all()
    for a in appointments:
        patient = Patient.query.get(a.patient_ID)
        a.patient_name = patient.name if patient else "Unknown"
    return render_template('doctor_dashboard.html', doctorn=doctor.name, doctor=doctor, appointments=appointments)

@app.route('/doctor/dashboard/viewpatient/<patient_id>')
def view_patient(patient_id):
    appt = Appointment.query.filter_by(patient_ID=patient_id).first()
    return render_template('viewpatient.html', patient=Patient.query.get(patient_id), appointment=appt, treatment=Treatment.query.filter_by(appointment_ID=appt.appointment_ID).first() if appt else None)

@app.route('/doctor/dashboard/appointment/complete/<int:appointment_id>')
def complete_appointment(appointment_id):
    appt = Appointment.query.get(appointment_id); appt.status = "Completed"; db.session.commit()
    doc = Doctor.query.get(appt.doctor_ID)
    return render_template('doctor_dashboard.html', doctorn=doc.name, doctor=doc, appointments=Appointment.query.filter_by(doctor_ID=doc.doctor_ID).all())

@app.route('/doctor/dashboard/appointment/cancel/<int:appointment_id>')
def cancel_appointment(appointment_id):
    appt = Appointment.query.get(appointment_id); appt.status = "Cancelled"; db.session.commit()
    doc = Doctor.query.get(appt.doctor_ID)
    return render_template('doctor_dashboard.html', doctorn=doc.name, doctor=doc, appointments=Appointment.query.filter_by(doctor_ID=doc.doctor_ID).all())

@app.route('/doctor/add_prescription/<int:appointment_id>', methods=['GET', 'POST'])
def add_prescription(appointment_id):
    appt = Appointment.query.get(appointment_id); doctor = Doctor.query.get(appt.doctor_ID); patient = Patient.query.get(appt.patient_ID)
    treatment = Treatment.query.filter_by(appointment_ID=appointment_id).first()
    if request.method == 'GET':
        return render_template("add_prescription.html", doctor=doctor, patient=patient, appointment=appt, treatment=treatment)
    new_treat = Treatment(appointment_ID=appointment_id, prescription=request.form['prescription'], diagnosis=request.form['diagnosis'], notes=request.form['notes'])
    db.session.add(new_treat); appt.status = "Completed"; db.session.commit()
    return render_template("prescription.html", doctor=doctor, patient=patient, appointment=appt, treatment=new_treat)

# ================= PATIENT SECTION =================

@app.route("/patient/login",methods=['GET','POST'])
def patient_login():
    if request.method=='GET':
        return render_template("patient_login.html")
    patient = Patient.query.filter_by(name=request.form['name'], password=request.form['password']).first()
    if not patient:
        return render_template("patient_login.html", error="Invalid Credentials")
    appointments = Appointment.query.filter_by(patient_ID=patient.patient_ID).all()
    for a in appointments:
        doc = Doctor.query.get(a.doctor_ID)
        a.doctor_name = doc.name if doc else "Unknown"
    return render_template("patient_dashboard.html", patient=patient, departments=Department.query.all(), appointments=appointments, upcoming_appointments=[a for a in appointments if a.status=="Upcoming"], previous_appointments=[a for a in appointments if a.status in["Completed","Cancelled"]])

@app.route("/patient/register", methods=['GET','POST'])
def patient_registration():
    if request.method == 'GET':
        return render_template("patient_registration.html")
    new = Patient(password=request.form['password'], name=request.form['name'], contact=request.form['contact'])
    db.session.add(new); db.session.commit()
    return render_template('patient_registration_success.html', patientn=new.name)

@app.route("/patient/dashboard/<patient_id>")
def patient_dashboard(patient_id):
    patient = Patient.query.get(patient_id); appointments = Appointment.query.filter_by(patient_ID=patient.patient_ID).all()
    for a in appointments:
        doc = Doctor.query.get(a.doctor_ID)
        a.doctor_name = doc.name if doc else "Unknown"
    return render_template("patient_dashboard.html", patient=patient, departments=Department.query.all(), appointments=appointments, upcoming_appointments=[a for a in appointments if a.status=="Upcoming"], previous_appointments=[a for a in appointments if a.status in["Completed","Cancelled"]])

@app.route("/patient/update/<int:patient_ID>", methods=['GET', 'POST'])
def update_patient(patient_ID):
    patient = Patient.query.get(patient_ID)

    if request.method == "POST":
        patient.name = request.form["name"]
        patient.contact = request.form["contact"]
        patient.age = request.form["age"]
        db.session.commit()

        return render_template("patient_update_success.html", name=patient.name, patient_ID=patient_ID)

    return render_template("patient_update.html", patient=patient)

@app.route("/patient/dashboard/<patient_id>/department/<department_id>")
def patient_dashboard_department(patient_id, department_id):
    dept = Department.query.get(department_id); doctors = [d for d in Doctor.query.all() if d.specialisation and d.specialisation.strip()==dept.name.strip()]
    return render_template("department.html", department=dept, doctors=doctors, patient_ID=patient_id)

@app.route("/patient/book_appointment/<patient_id>/<doctor_id>", methods=['GET','POST'])
def book_appointment(patient_id, doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if request.method == 'GET':
        return render_template("appointment.html", doctor=doctor, availability=doctor.availability, patient_id=patient_id)
    new_appt = Appointment(patient_ID=patient_id, doctor_ID=doctor_id, date=request.form['day'], time=request.form['time'], status="Upcoming")
    db.session.add(new_appt); db.session.commit()
    return render_template("appointment_success.html", doctorn=doctor.name, availability=f"{request.form['day']}, {request.form['time']}")

@app.route('/patient/prescription/<int:appointment_id>')
def patient_view_prescription(appointment_id):
    appt = Appointment.query.get(appointment_id)
    return render_template('prescription.html', doctor=Doctor.query.get(appt.doctor_ID), patient=Patient.query.get(appt.patient_ID), appointment=appt, treatment=Treatment.query.filter_by(appointment_ID=appointment_id).first())

@app.route('/patient/dashboard/appointment/cancel/<int:appointment_id>')
def patient_cancel(appointment_id):
    appt = Appointment.query.get(appointment_id); appt.status="Cancelled"; db.session.commit()
    patient = Patient.query.get(appt.patient_ID); appointments = Appointment.query.filter_by(patient_ID=patient.patient_ID).all()
    return render_template('patient_dashboard.html', patient=patient, departments=Department.query.all(), appointments=appointments, upcoming_appointments=[a for a in appointments if a.status=="Upcoming"], previous_appointments=[a for a in appointments if a.status in["Completed","Cancelled"]])

if __name__ == '__main__':
    app.run(debug=True)



