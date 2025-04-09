"""
WSGI entry point for the application.
This file is used by Render.com to start the application.
"""
import os

# Configure icecream before importing any modules that use it
from ic_config import configure_icecream
configure_icecream()

from flask_migrate import Migrate
from apps.config import config_dict
from apps import create_app, db

# Determine the environment
DEBUG = os.getenv("DEBUG_MODE", "False") == "True"
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production]')

# Create the Flask application
app = create_app(app_config)
Migrate(app, db)

# Initialize the database if needed
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization error: {str(e)}")

if __name__ == "__main__":
    app.run()
