from flask import Blueprint
from flask import request, render_template
from mongo_connect import db, mongo_jsonify

sh_bp = Blueprint('sh_bp', __name__)
# Social History Functionality
@sh_bp.route('/socialhistory', methods=['GET', 'POST'])
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

@sh_bp.route('/socialhistory', methods=['PUT'])
def handle_social_history_put():
    data = request.json
    return update_social_history(data)
    
@sh_bp.route('/patient_socialhistory', methods=['GET'])
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
