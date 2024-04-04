from flask import render_template, redirect, request, url_for, flash
from apps.home import blueprint
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps import db

from apps.home.models import ScanLog
# from apps.home.util import verify_pass, create_default_admin

from icecream import ic
from sqlalchemy.exc import IntegrityError


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

