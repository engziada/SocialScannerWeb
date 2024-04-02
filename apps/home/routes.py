from flask import render_template, redirect, request, url_for, flash
from apps.home import blueprint
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps import db

from apps.home.forms import InfluencerForm, SubProfileForm
from apps.home.models import Influencer, Subprofile, ScanLog
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

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@blueprint.route("/influencers")
# @login_required
def influencers():
    influencers = Influencer.query.all()  # Fetch all influencers
    return render_template("home/influencers.html", influencers=influencers)


@blueprint.route("/influencer_add", methods=["GET", "POST"])
# @login_required
def influencer_add():
    form = InfluencerForm(request.form)  # Create an instance of the form
    if form.validate_on_submit():
        new_influencer = Influencer(
            full_name=form.full_name.data,
            gender=form.gender.data,
            country=form.country.data,
            city=form.city.data,
            phone=form.phone.data,
            email=form.email.data,
        )
        ic(form.profile_picture.data)
        if form.profile_picture.data:
            new_influencer.save_profile_picture(form.profile_picture.data)

        db.session.add(new_influencer)
        db.session.commit()
        flash("Influencer created successfully!", "success")
        return redirect(url_for("home_blueprint.influencers"))
    return render_template("home/influencer_add.html", form=form)


# You can add similar routes for other functionalities


@blueprint.route("/influencer/<int:influencer_id>")
# @login_required
def influencer_details(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("home_blueprint.influencers"))
    return render_template("home/influencer_details.html", influencer=influencer)


@blueprint.route("/influencer_delete/<int:influencer_id>")
# @login_required
def influencer_delete(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("home_blueprint.influencers"))
    db.session.delete(influencer)
    db.session.commit()
    flash("Influencer deleted successfully!", "success")
    return redirect(url_for("home_blueprint.influencers"))