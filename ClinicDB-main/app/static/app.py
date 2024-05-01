import base64
from flask import Flask, request, render_template, jsonify, Response, redirect, url_for
from pymongo import MongoClient
import os
from flask_cors import CORS
from bson import ObjectId
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Use environment variables for sensitive information
username = os.getenv('MONGO_USERNAME')  # Set this in your environment
password = os.getenv('MONGO_PASSWORD')  # Set this in your environment
print("Username:", username)
print("Password:", password)
dbname = "clinics"
cluster_url = "cluster0.jmmyofl.mongodb.net"

# Corrected MongoClient initialization
client = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_url}/{dbname}?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = client[dbname]

def mongo_jsonify(data):
    class MongoEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    return Response(
        json.dumps(data, cls=MongoEncoder),
        mimetype='application/json'
    )

def mongo_jsonify_list(data_list):
    class MongoEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    formatted_data = [MongoEncoder().encode(item) for item in data_list]
    return Response(
        f'[{", ".join(formatted_data)}]',
        mimetype='application/json'
    )

@app.route('/', methods=['GET', 'POST', 'DELETE', 'PUT'])
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

@app.route('/patient', methods=['GET'])
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

@app.route('/visit-form-lookup')
def visit_form_lookup_page():
    return render_template('visit_form_lookup.html')

@app.route('/update-visit-form')
def update_visit_form_page():
    return render_template('update_visit_form.html')

@app.route('/lookup', methods=['POST'])
def lookup_visit_form():
    form_id = request.form.get('form_id')
    visit_form = db.visit_form.find_one({'RecordID': form_id})
    if visit_form and 'VisitFormImg' in visit_form:
        visit_form['VisitFormImg'] = base64.b64encode(visit_form['VisitFormImg']).decode('utf-8')
    return render_template('visit_form.html', visit_form=visit_form)

UPLOAD_FOLDER = 'uploads'
@app.route('/update-visit-form', methods=['POST'])
def update_visit_form():
    record_id = request.form.get('record_id')

    # Ensure the visit form exists
    visit_form = db.visit_form.find_one({'RecordID': record_id})
    if not visit_form:
        return 'Visit form not found', 404

    # Process the image fields
    for image_field in ['new_visit_form_image', 'new_mental_health_image']:
        image_file = request.files.get('new_visit_form_image')
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_file_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(image_file_path)

            with open(image_file_path, 'rb') as file:
                binary_data = file.read()
            os.remove(image_file_path)  # Remove the file after reading

            # Update the corresponding image field in MongoDB
            db_field = 'VisitFormImg' if image_field == 'new_visit_form_image' else 'MentalHealthImg'
            db.visit_form.update_one(
                {'RecordID': record_id},
                {'$set': {db_field: binary_data}}
            )

    # Update other fields
    update_fields = {
        'PatientID': request.form.get('patient_id'),
        'Date': request.form.get('date'),
        'ClinicID': request.form.get('clinic_id')
    }
    for field, value in update_fields.items():
        if value:
            db.visit_form.update_one(
                {'RecordID': record_id},
                {'$set': {field: value}}
            )

    #return redirect(url_for('update_visit_form_page'))
    return redirect(url_for('visit_form_lookup_page'))

@app.route('/add-visit-form', methods=['POST'])
def add_visit_form():
    record_id = request.form['record_id']
    patient_id = request.form['patient_id']
    date = request.form['date']
    clinic_id = request.form['clinic_id']

    visit_form_image = request.files['visit_form_image']
    mental_health_image = request.files['mental_health_image']

    # Convert images to binary
    visit_form_img_data = visit_form_image.read() if visit_form_image else None
    mental_health_img_data = mental_health_image.read() if mental_health_image else None

    new_visit_form = {
        'RecordID': record_id,
        'PatientID': patient_id,
        'Date': date,
        'VisitFormImg': visit_form_img_data,
        'MentalHealthImg': mental_health_img_data, 
        'ClinicID': clinic_id
    }

    # Insert the new visit form into MongoDB
    db.visit_form.insert_one(new_visit_form)

    return redirect(url_for('visit_form_lookup_page'))

# Social History Functionality
@app.route('/socialhistory', methods=['GET', 'POST'])
def social_history_index():
    # TO DO
    # GET request: Fetching social history by patient's first and last name
    if request.method == 'GET' and 'first_name' in request.args and 'last_name' in request.args:
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        patient = db.patient.find_one({'FirstName': first_name, 'LastName': last_name})
        if patient:
            patient_id = patient['PatientID']
            social_history_data = db.social_history.find_one({'PatientID': patient_id})
            return mongo_jsonify(social_history_data) if social_history_data else "Patient's social history was not found (1)"
        else:
            return "Patient not found"
    
    # POST request: Adding a new clinic or searching by name
    elif request.method == 'POST':
        if 'update' in request.form:
            return update_social_history(request.form)
        else:
            return add_patient_social_history(request.form)

    # PUT request
    elif request.method == 'PUT':
        return update_social_history(request.json)

    return render_template('social_history_index.html')

@app.route('/socialhistory', methods=['PUT'])
def handle_social_history_put():
    data = request.json
    return update_social_history(data)
    
@app.route('/patient_socialhistory', methods=['GET'])
def get_social_history():
    patient_id = request.args.get('patient_id')
    social_history_data = db.social_history.find_one({'PatientID': patient_id})
    return mongo_jsonify(social_history_data) if social_history_data else "Patient's social history was not found (2)"

def search_social_history(data):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    patient_id  = db.patient.find_one({'FirstName': first_name, 'LastName': last_name})
    social_history_data = db.social_history.find_one({'PatientID': patient_id})
    return mongo_jsonify(social_history_data) if social_history_data else "Patient's social history was not found (3)"
    
def add_patient_social_history(data):
    # Add new patient
    patient_id = data.get('PatientID')
    existing_patient_social_history = db.social_history.find_one({'PatientID': patient_id})

    if existing_patient_social_history:
        return "Social history already exists for the patient"
    else:
        new_patient_social_history = {
            "Alcohol": data.get('Alcohol'),
            "Tobacco": data.get('Tobacco'),
            "Drugs": data.get('Drugs'),
            "LivingArrangements": data.get('LivingArrangements'),
            "Immunization": data.get('Immunization'),
            "PatientID": data.get('PatientID') ,
            "SocialHistoryID": data.get('SocialHistoryID'),
        }
        db.social_history.insert_one(new_patient_social_history)
        return "Patient social history added successfully"

def update_social_history(data):
    patient_id = data.get('patient_id')
    existing_patient = db.patient.find_one({'PatientID': patient_id})
    if existing_patient:
        update_data = {}

        # Define a mapping from the form field names to the database field names
        field_mapping = {
            'new_alcohol': 'Alcohol',
            'new_tobacco': 'Tobacco',
            'new_drugs': 'Drugs',
            'new_living_arrangements': 'LivingArrangements',
            'new_immunization': 'Immunization',
            'new_social_history_id': 'SocialHistoryID'
        }

        for form_field, db_field in field_mapping.items():
            if data.get(form_field):
                update_data[db_field] = data[form_field]

        # Perform the update operation in MongoDB if there is data to update
        if update_data:
            db.social_history.update_one({'PatientID': patient_id}, {'$set': update_data})
            return "Patient social history updated successfully"
        else:
            return "No social history data provided for update"
    else:
        return "No patient found with the specified ID"

@app.route('/drughistory', methods=['GET', 'POST'])
def drughistory():
    # GET request: Fetching a patient's drug history by patient ID
    if request.method == 'GET' and 'first_name' in request.args and 'last_name' in request.args:
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        patient_data = db.patient.find_one({'FirstName': first_name, 'LastName': last_name})
        if patient_data:
            patient_id = patient_data['PatientID']
            drug_history_data = list(db.drug_history.find({'PatientID': patient_data['PatientID']}))
            return mongo_jsonify_list(drug_history_data) if drug_history_data else "No drug history found"
        else:
            return "No patient found with the specified name"

    # POST requests: Adding a new patient or searching by name
    elif request.method == 'POST':
            add_drug_history(request.form)

    # PUT request
    elif request.method == 'PUT':
        return update_drug_history(request.json)

    return render_template('drughistory.html')

@app.route('/drughistory', methods=['PUT'])
def handle_put_drug_history():
    data = request.json
    return update_drug_history(data)

def search_drug_history(data):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    patient_data = db.patient.find_one({'FirstName': first_name, 'LastName': last_name})
    drug_history_data = db.drug_history.find_one({'PatientID': patient_data})
    return mongo_jsonify(drug_history_data) if drug_history_data else "No drug history found"
    
def add_drug_history(data):
    print("Enter add_drug_history")
    patient_id = data.get('Patient_id_upload')
    dh_id = data.get('Drughistory_id_upload')
    existing_drug_history = db.drug_history.find_one({'DrugHistoryID': dh_id, 'PatientID': patient_id})
    existing_patient = db.patient.find_one({'PatientID': patient_id})
    if existing_patient:
        if existing_drug_history:
            print("Enter if statement add_drug_history")
            return "Drug history already exists for the patient"
        else:
            print("Enter else statement add_drug_history")
            new_drug_history = {
                "Problem": data.get('Problem'),
                "Medication": data.get('Medication'),
                "Dosage": data.get('Dosage'),
                "DateReviewed": data.get('Date_reviewed'),
                "PatientID": data.get('Patient_id_upload'),
                "DrugHistoryID": data.get('Drughistory_id_upload')
            }
            db.drug_history.insert_one(new_drug_history)
            return "Drug History added successfully"
    else:
        return "No patient found with the specified ID"

def update_drug_history(data):
    patient_id = data.get('patient_id_update')
    existing_patient = db.patient.find_one({'PatientID': patient_id})
    dh_id = data.get('drughistory_id_update')
    existing_dh = db.drug_history.find_one({'PatientID': patient_id, 'DrugHistoryID': dh_id})

    if existing_patient:
        if existing_dh:
            update_data = {}

            # Define a mapping from the form field names to the database field names
            field_mapping = {
                'new_problem': 'Problem',
                'new_medication': 'Medication',
                'new_dosage': 'Dosage',
                'new_date_reviewed': 'DateReviewed',
                'patient_id': 'PatientID',
                'drughistory_id_update': 'DrugHistoryID'
            }

            for form_field, db_field in field_mapping.items():
                if data.get(form_field):
                    update_data[db_field] = data[form_field]

            # Perform the update operation in MongoDB if there is data to update
            if update_data:
                db.drug_history.update_one({'PatientID': patient_id, 'DrugHistoryID': dh_id}, {'$set': update_data})
                return "Drug history data updated successfully"
            else:
                return "No data provided for update"
        else:
            return "No drug history found with the specified ID"
    else:
        return "No patient found with the specified ID"

@app.route('/healthhistory', methods=['GET', 'POST'])
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

@app.route('/healthhistory', methods=['PUT'])
def handle_health_history_put():
    data = request.json
    return update_health_history(data)

@app.route('/patienthealthhistory', methods=['GET'])
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

if __name__ == '__main__':
    app.run(debug=True)