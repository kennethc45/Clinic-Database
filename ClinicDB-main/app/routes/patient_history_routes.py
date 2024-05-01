from flask import Blueprint
from flask import request, render_template
from mongo_connect import db, mongo_jsonify

patient_bp = Blueprint('patient_bp', __name__)

@patient_bp.route('/', methods=['GET', 'POST', 'DELETE', 'PUT'])
def index():
    # GET request: Fetching a patient by ID
    if request.method == 'GET' and 'patient_id' in request.args:
        return get_patient()

    # POST request: Adding a new patient or searching by name
    elif request.method == 'POST':
        action = request.form.get('action')
        print("Form data:", request.form)
        if action == 'add_patient':
            # Pass request.form as the argument to add_patient
            return add_patient(request.form)
        elif action == 'search_patient':
            return search_patient(request.form)

    # DELETE request
    elif request.method == 'DELETE':
        return delete_patient(request.json)

    # PUT request
    elif request.method == 'PUT':
        print("PUT request data:", request.json)
        return update_patient(request.json)

    return render_template('index.html')

@patient_bp.route('/patient', methods=['GET'])
def get_patient():
    patient_id = request.args.get('patient_id')
    patient_data = db.patient.find_one({'PatientID': patient_id})
    return mongo_jsonify(patient_data) if patient_data else "No patient found"

def search_patient(data):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    patient_data = db.patient.find_one({'FirstName': first_name, 'LastName': last_name})
    return mongo_jsonify(patient_data) if patient_data else "No patient found"

def add_patient(data):
    patient_id = data.get('patient_id')
    existing_patient = db.patient.find_one({'PatientID': patient_id})
    if existing_patient:
        return "Patient with the specified ID already exists"
    else:
        # Extract patient data from the form
        new_patient_data = {
            'PatientID': data.get('patient_id'),
            'LastName': data.get('last_name'),
            'FirstName': data.get('first_name'),
            'Sex': data.get('sex'),
            'DateOfBirth': data.get('date_of_birth'),
            'VeteranFlag': data.get('veteran_flag') == 'on',
            'Alias': data.get('alias'),
            'Ethnicity': data.get('ethnicity'),
            'PhoneNumber': data.get('phone_number'),
            'Address': data.get('address'),
            'PCP_ID': data.get('pcp_id'),
            'Insurance': data.get('insurance'),
            'WaiverForm': data.get('waiver_form')
        }

        # Optional: Validate the new patient data here

        # Insert the new patient into MongoDB
        db.patient.insert_one(new_patient_data)
        return "New patient added successfully"

def update_patient(data):
    patient_id = data.get('patient_id')
    existing_patient = db.patient.find_one({'PatientID': patient_id})
    if existing_patient:
        update_data = {}

        # Define a mapping from the form field names to the database field names
        field_mapping = {
            'new_first_name': 'FirstName',
            'new_last_name': 'LastName',
            'new_sex': 'Sex',
            'new_date_of_birth': 'DateOfBirth',
            'new_veteran_flag': 'VeteranFlag',
            'new_alias': 'Alias',
            'new_ethnicity': 'Ethnicity',
            'new_phone_number': 'PhoneNumber',
            'new_address': 'Address',
            'new_PCP_ID': 'PCP_ID',
            'new_insurance': 'Insurance',
            'new_waiver_form': 'WaiverForm'
        }

        for form_field, db_field in field_mapping.items():
            if data.get(form_field):
                update_data[db_field] = data[form_field]

        # Perform the update operation in MongoDB if there is data to update
        if update_data:
            db.patient.update_one({'PatientID': patient_id}, {'$set': update_data})
            return "Patient data updated successfully"
        else:
            return "No data provided for update"
    else:
        return "No patient found with the specified ID"

def delete_patient(data):
    patient_id = data.get('PatientID')
    print("Patient ID to delete:", patient_id)  # Debug print
    existing_patient = db.patient.find_one({'PatientID': patient_id})
    if existing_patient:
        db.patient.delete_one({'PatientID': patient_id})
        return "Patient data deleted successfully"
    else:
        return "No patient found with the specified ID"