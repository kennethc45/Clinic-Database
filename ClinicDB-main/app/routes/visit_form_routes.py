from flask import Blueprint
from flask import request, render_template
import base64
from flask import request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from mongo_connect import db, mongo_jsonify

vf_bp = Blueprint('vf_bp', __name__)

@vf_bp.route('/visit-form-lookup')
def visit_form_lookup_page():
    return render_template('visit_form_lookup.html')

@vf_bp.route('/update-visit-form')
def update_visit_form_page():
    return render_template('update_visit_form.html')

@vf_bp.route('/lookup', methods=['POST'])
def lookup_visit_form():
    form_id = request.form.get('form_id')
    visit_form = db.visit_form.find_one({'RecordID': form_id})
    if visit_form and 'VisitFormImg' in visit_form:
        visit_form['VisitFormImg'] = base64.b64encode(visit_form['VisitFormImg']).decode('utf-8')
    return render_template('visit_form.html', visit_form=visit_form)

UPLOAD_FOLDER = 'uploads'
@vf_bp.route('/update-visit-form', methods=['POST'])
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
    return redirect(url_for('vf_bp.visit_form_lookup_page'))

@vf_bp.route('/add-visit-form', methods=['POST'])
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

    return redirect(url_for('vf_bp.visit_form_lookup_page'))