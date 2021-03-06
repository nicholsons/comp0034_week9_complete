import os
from pathlib import Path
import pandas as pd
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
photos = UploadSet('photos', IMAGES)


def create_app(config_classname):
    """
    Initialise and configure the Flask application.
    :type config_classname: Specifies the configuration class
    :rtype: Returns a configured Flask object
    """
    app = Flask(__name__)
    app.config.from_object(config_classname)

    db.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    csrf.init_app(app)
    configure_uploads(app, photos)

    with app.app_context():
        from my_app.models import User, Profile, Area
        db.create_all()

        # Add the local authority data to the database (this is a workaround you don't need this for your coursework!)
        data_path = app.config['DATA_PATH']
        csv_file = Path(data_path).joinpath('household_recycling.csv')
        la_data = pd.read_csv(csv_file, usecols=['Code', 'Area'])
        la_data.drop_duplicates(inplace=True)
        la_data.set_index('Code', inplace=True)
        la_data.to_sql('area', db.engine, if_exists='replace')

        from dash_app.dash import init_dashboard
        app = init_dashboard(app)

    from my_app.main.routes import main_bp
    app.register_blueprint(main_bp)

    from my_app.community.routes import community_bp
    app.register_blueprint(community_bp)

    from my_app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
