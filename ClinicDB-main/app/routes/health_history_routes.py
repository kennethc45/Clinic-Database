from flask import Blueprint
from flask import request, render_template
from mongo_connect import db, mongo_jsonify

hh_bp = Blueprint('dh_bp', __name__)

@hh_bp.route('/healthhistory', methods=['GET', 'POST'])
def health_history_index():
    # GET request: Fetching a patient by ID
    if request.method == 'GET' and 'patient_id' in request.args:
        patient_id = request.args.get('patient_id')
        patient = db.patient.find_one({'PatientID': patient_id})
        if patient:
            health_history_data = db.health_history.find_one({'PatientID': patient_id})
            return mongo_jsonify(health_history_data) if health_history_data else "Patient has no health history"
        else:
            return "Patient not found"
    elif request.method == 'POST':
        if 'update' in request.form:
            return update_health_history(request.form)
        else:
            return add_health_history(request.form)

    # PUT request
    elif request.method == 'PUT':
        return update_health_history(request.json)

    return render_template('healthhistory.html')

@hh_bp.route('/healthhistory', methods=['PUT'])
def handle_health_history_put():
    data = request.json
    return update_health_history(data)

@hh_bp.route('/patienthealthhistory', methods=['GET'])
def get_health_history():
    patient_id = request.args.get('patient_id')
    health_history_data = db.health_history.find_one({'PatientID': patient_id})
    return mongo_jsonify(health_history_data) if health_history_data else "No health history found"

def search_health_history(data):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    patient_id  = db.patient.find_one({'FirstName': first_name, 'LastName': last_name})
    health_history_data = db.health_history.find_one({'PatientID': patient_id})
    return mongo_jsonify(health_history_data) if health_history_data else "Patient's health history was not found"

def add_health_history(data):
    patient_id = data.get('patient_id')
    existing_health_history = db.health_history.find_one({'PatientID': patient_id})
    
    if existing_health_history:
        return "Health history already exists for the patient"
    
    else:
        new_health_history = {
            'RecievedMedication': data.get('add_received_medication'),
            'Allergies': data.get('add_allergies'),
            'DiagnosisConditions': data.get('add_diagnosis_and_conditions'),
            'FamilyHistory': data.get('add_family_history'),
            'PatientID': patient_id,
            'HealthHistoryID': data.get('add_health_history_id'),
        }
    
        db.health_history.insert_one(new_health_history)
        return "Health history added successfully"

def update_health_history(data):
    patient_id = data.get('patient_id')
    existing_health_history = db.health_history.find_one({'PatientID': patient_id})
    if existing_health_history:
        update_data = {}

        # Define a mapping from the form field names to the database field names
        field_mapping = {
            'new_received_medication': 'RecievedMedication',
            'new_allergies': 'Allergies',
            'new_diagnosis_conditions': 'DiagnosisConditions',
            'new_family_history': 'FamilyHistory',
            'new_health_history_id': 'HealthHistoryID'
        }

        for form_field, db_field in field_mapping.items():
            if data.get(form_field):
                update_data[db_field] = data[form_field]

        # Perform the update operation in MongoDB if there is data to update
        if update_data:
            db.health_history.update_one({'PatientID': patient_id}, {'$set': update_data})
            return "Patient health history updated successfully"
        else:
            return "No health history data provided for update"
    else:
        return "No patient found with the specified ID"
    
pcp_bp = Blueprint('pcp_bp', __name__) 

@pcp_bp.route('/pcp', methods=['GET', 'POST'])
def pcp_index():
    # GET request: Fetching a patient by ID
    if request.method == 'GET' and 'first_name' in request.args and 'last_name' in request.args:
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        patient = db.patient.find_one({'FirstName': first_name, 'LastName': last_name})
        if patient:
            pcp_id = patient.get('PCP_ID')
            pcp_data = db.pcp.find_one({'PCP_ID': pcp_id})
            return mongo_jsonify(pcp_data) if pcp_data else "Patient has no PCP"
        else:
            return "Patient not found"
    elif request.method == 'POST':
        if 'update' in request.form:
            return update_pcp(request.form)
        else:
            return add_pcp(request.form)

    # PUT request
    elif request.method == 'PUT':
        return update_pcp(request.json)

    return render_template('pcp.html')

@pcp_bp.route('/pcp', methods=['PUT'])
def handle_pcp_put():
    data = request.json
    return update_pcp(data)

@pcp_bp.route('/patientpcp', methods=['GET'])
def get_pcp():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    patient = db.patient.find_one({'PatientID': patient_id})
    pcp_id = patient.get('PCP_ID')
    pcp_data = db.pcp.find_one({'PCP_ID': pcp_id})
    return mongo_jsonify(pcp_data) if pcp_data else "No PCP found"

def add_pcp(data):
    pcp_id = data.get('pcp_id')
    existing_pcp = db.pcp.find_one({'PCP_ID': pcp_id})

    if existing_pcp:
        return "PCP already exists"

    else:
        new_pcp = {
            'PCP_ID': pcp_id,
            'PhysicianName': data.get('add_pcp_name'),
            'PhysicianLocation': data.get('add_pcp_location'),
            'PhysicianPhone': data.get('add_pcp_phone'),
        }

        db.pcp.insert_one(new_pcp)
        return "PCP added successfully"

def update_pcp(data):
    pcp_id = data.get('pcp_id')
    existing_pcp = db.pcp.find_one({'PCP_ID': pcp_id})
    if existing_pcp:
        update_data = {}

        # Define a mapping from the form field names to the database field names
        field_mapping = {
            'new_pcp_name': 'PhysicianName',
            'new_pcp_location': 'PhysicianLocation',
            'new_pcp_phone': 'PhysicianPhone',
        }

        for form_field, db_field in field_mapping.items():
            if data.get(form_field):
                update_data[db_field] = data[form_field]

        # Perform the update operation in MongoDB if there is data to update
        if update_data:
            db.pcp.update_one({'PCP_ID': pcp_id}, {'$set': update_data})
            return "PCP information updated successfully"
        else:
            return "No PCP data provided for update"
    else:
        return "No PCP found with the specified ID"