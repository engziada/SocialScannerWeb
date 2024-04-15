from flask import render_template, request, flash, session
from apps.home import blueprint
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps.home.models import Log
from apps.home.forms import SearchForm

from apps.home.util import search_user_profile
from apps.social.models import Platform, SocialAccount
# from apps.home.util import verify_pass, create_default_admin

from icecream import ic


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


#////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/log")
# @login_required
def log():
    logs = Log.query.all()  # Fetch all influencers
    return render_template("home/log.html", logs=logs)

#////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/search", methods=["GET", "POST"])
# @login_required
def search():
    form = SearchForm()
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]

    profile_data = None

    if form.validate_on_submit():
        platform = form.platform.data
        username = form.username.data

        try:
            profile_data = search_user_profile(username, platform)
            if profile_data.get("error") is not None:
                flash(profile_data["error"], "danger")
            existingRecord = SocialAccount.query.filter_by(username=username, platform_id=platform).first() is not None
            profile_data["existing_record"] = existingRecord
            if profile_data and not existingRecord:
                session["profile_data"] = profile_data
        except Exception as e:
            flash(f"Error: {str(e)}")  # Handle backend errors gracefully

    return render_template("home/search.html", form=form, profile_data=profile_data)


# ////////////////////////////////////////////////////////////////////////////////////////