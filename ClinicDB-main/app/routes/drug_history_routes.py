from flask import Blueprint
from flask import request, render_template
from mongo_connect import db, mongo_jsonify, mongo_jsonify_list

dhst_bp = Blueprint('dhst_bp', __name__)

@dhst_bp.route('/drughistory', methods=['GET', 'POST'])
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

@dhst_bp.route('/drughistory', methods=['PUT'])
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