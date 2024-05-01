from flask import Flask, Response
from bson import ObjectId
import json
import os

# Import parts of our application

from .routes.patient_history_routes import patient_bp
from .routes.visit_form_routes import vf_bp
from .routes.health_history_routes import hh_bp, pcp_bp
from .routes.drug_history_routes import dhst_bp   
from .routes.social_history_routes import sh_bp

def create_app():
    app = Flask(__name__)
    with app.app_context():
  
        # Register Blueprints
        app.register_blueprint(patient_bp, url_prefix='')
        app.register_blueprint(vf_bp)
        app.register_blueprint(hh_bp)
        app.register_blueprint(dhst_bp)
        app.register_blueprint(sh_bp)
        app.register_blueprint(pcp_bp)

        return app
