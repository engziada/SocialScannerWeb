from flask import render_template, redirect, request, url_for, flash
from apps.home import blueprint
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps import db

from apps.home.forms import InfluencerForm, SocialAccountForm
from apps.home.models import Influencer, SocialAccount, ScanLog
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

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@blueprint.route("/influencers")
# @login_required
def influencers():
    influencers = Influencer.query.all()  # Fetch all influencers
    return render_template("home/influencers.html", influencers=influencers)


@blueprint.route("/influencer_add", methods=["GET", "POST"])
# @login_required
def influencer_add():
    form = InfluencerForm()  # Create an instance of the form
    if form.validate_on_submit():
        new_influencer = Influencer(
            full_name=form.full_name.data,
            gender=form.gender.data,
            country=form.country.data,
            city=form.city.data,
            phone=form.phone.data,
            email=form.email.data,
            profile_picture=None,  # Set a default value initially
        )
        
        if form.profile_picture.data:
            new_influencer.save_profile_picture(form.profile_picture.data)

        db.session.add(new_influencer)
        db.session.commit()
        flash("Influencer created successfully!", "success")
        return redirect(url_for("home_blueprint.socialaccount_add", influencer_id=new_influencer.id))
    return render_template("home/influencer_add.html", form=form)


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


@blueprint.route("/influencer_edit/<int:influencer_id>", methods=["GET", "POST"])
# @login_required
def influencer_edit(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("home_blueprint.influencers"))

    form = InfluencerForm(obj=influencer)  # Create an instance of the form
    if form.validate_on_submit():
        influencer.full_name=form.full_name.data
        influencer.gender=form.gender.data
        influencer.country=form.country.data
        influencer.city=form.city.data
        influencer.phone=form.phone.data
        influencer.email=form.email.data
        influencer.profile_picture=form.profile_picture.data

        if form.profile_picture.data:
            influencer.save_profile_picture(form.profile_picture.data)

        db.session.commit()
        flash("Influencer updated successfully!", "success")
        return redirect(url_for("home_blueprint.influencers"))
    
    return render_template("home/influencer_edit.html", form=form, influencer=influencer)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/socialaccounts/<int:influencer_id>")
# @login_required
def socialaccounts(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("home_blueprint.influencers"))

    socialaccounts = SocialAccount.query.filter_by(influencer_id=influencer_id).all()  # Fetch social accounts for a specific influencer
    return render_template("home/socialaccounts.html", socialaccounts=socialaccounts, influencer=influencer)


@blueprint.route("/socialaccount_add/<int:influencer_id>", methods=["GET", "POST"])
# @login_required
def socialaccount_add(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("home_blueprint.influencers"))
    
    form = SocialAccountForm()  # Create an instance of the form
    if form.validate_on_submit():
        try:
            new_socialaccount = SocialAccount(
                influencer_id=influencer_id,
                platform=form.platform.data,
                username=form.username.data,
                content_type=form.content_type.data,
                description=form.description.data,
                profile_picture=None,  # Set a default value initially
            )

            if form.profile_picture.data:
                new_socialaccount.save_profile_picture(form.profile_picture.data)

            db.session.add(new_socialaccount)
            db.session.commit()
            flash("Social Account created successfully!", "success")
            return redirect(url_for("home_blueprint.socialaccounts", influencer_id=influencer_id))
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists!", "danger")
    return render_template("home/socialaccount_add.html", form=form, influencer=influencer)


@blueprint.route("/socialaccount/<int:socialaccount_id>")
# @login_required
def socialaccount_details(socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("Social Account not found!", "danger")
        return redirect(url_for("home_blueprint.socialaccounts"))
    return render_template(
        "home/socialaccount_details.html", socialaccount=socialaccount)


@blueprint.route("/socialaccount_delete/<int:socialaccount_id>")
# @login_required
def socialaccount_delete(socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("Social Account not found!", "danger")
        return redirect(url_for("home_blueprint.socialaccounts"))
    db.session.delete(socialaccount)
    db.session.commit()
    flash("Social Account deleted successfully!", "success")


@blueprint.route("/socialaccount_edit/<int:socialaccount_id>", methods=["GET", "POST"])
# @login_required
def socialaccount_edit(socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("Social Account not found!", "danger")
        return redirect(url_for("home_blueprint.socialaccounts"))

    form = SocialAccountForm(obj=socialaccount)  # Create an instance of the form and populate it with existing data
    if form.validate_on_submit():
        socialaccount.platform = form.platform.data
        socialaccount.username = form.username.data
        socialaccount.content_type = form.content_type.data
        socialaccount.description = form.description.data

        if form.profile_picture.data:
            socialaccount.save_profile_picture(form.profile_picture.data)

        db.session.commit()
        flash("Social Account updated successfully!", "success")
        return redirect(url_for("home_blueprint.socialaccounts", influencer_id=socialaccount.influencer_id))

    return render_template("home/socialaccount_edit.html", form=form, socialaccount=socialaccount)

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////