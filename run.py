import os

from flask_migrate import Migrate
# from flask_minify  import Minify
from sys import exit

from apps.config import config_dict

# Configure icecream before importing any modules that use it
from ic_config import configure_icecream
configure_icecream()

from apps import create_app, db

from icecream import ic
from dotenv import load_dotenv

from flask_apscheduler import APScheduler

from tasks import scan_database

# dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
# load_dotenv(dotenv_path)

# Determine the environment and load the appropriate .env file
basedir = os.path.dirname(__file__)
if os.getenv("FLASK_ENV") == "development":
    dotenv_path = os.path.join(basedir , ".env.dev")
else:
    dotenv_path = os.path.join(basedir , ".env.prod")
load_dotenv(dotenv_path)

# WARNING: Don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG_MODE", "False") == "True"

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

ic(get_config_mode)

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError as e:
    msg = f"Error: Invalid <config_mode>. Expected values [Debug, Production], {e} "
    ic(msg)
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

# if not DEBUG:
#     Minify(app=app, html=True, js=False, cssless=False)
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

# Initialize scheduler instance
sched = APScheduler()

def scheduled_job():
    with app.app_context():  # noqa: F821
        scan_database(app, db.session)

# Configuring the scheduler
SCHEDULER_API_ENABLED = os.getenv("SCHEDULER_API_ENABLED", "True")
SCHEDULER_TRIGGER_HOUR = os.getenv("SCHEDULER_TRIGGER_HOUR", 0)
SCHEDULER_TRIGGER_MINUTE = os.getenv("SCHEDULER_TRIGGER_MINUTE", 0)
ic(SCHEDULER_API_ENABLED, SCHEDULER_TRIGGER_HOUR, SCHEDULER_TRIGGER_MINUTE)
app.config["SCHEDULER_API_ENABLED"] = SCHEDULER_API_ENABLED
app.config["JOBS"] = [
    {
        "id": "job1",
        "func": scheduled_job,
        "args": [],
        # "trigger": SCHEDULER_TRIGGER,
        # "seconds": 60,  # Run every hour (adjust as needed)
        "trigger": "cron",
        "hour": SCHEDULER_TRIGGER_HOUR,  # Run daily at midnight
        "minute": SCHEDULER_TRIGGER_MINUTE,
    }
]
sched.init_app(app)
# sched.add_job(id="scan", func=scheduled_job, trigger=CronTrigger(hour=6, minute=0))  # trigger="interval", seconds=10)#
# scheduled_job()
sched.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
    # app.run(debug=True)
