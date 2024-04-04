from flask import render_template, redirect, url_for, flash
from flask_wtf.file import FileField

from apps.profiles import blueprint

from apps import db

from apps.profiles.forms import InfluencerForm
from apps.profiles.models import Influencer

from icecream import ic
from werkzeug.datastructures import FileStorage


@blueprint.route("/influencers")
# @login_required
def influencers():
    influencers = Influencer.query.all()  # Fetch all influencers
    return render_template("profiles/influencers.html", influencers=influencers)


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
        return redirect(url_for("profiles_blueprint.socialaccount_add", influencer_id=new_influencer.id))
    return render_template("profiles/influencer_add.html", form=form)


@blueprint.route("/influencer/<int:influencer_id>")
# @login_required
def influencer_details(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("profiles_blueprint.influencers"))
    return render_template("profiles/influencer_details.html", influencer=influencer)


@blueprint.route("/influencer_delete/<int:influencer_id>")
# @login_required
def influencer_delete(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("profiles_blueprint.influencers"))
    db.session.delete(influencer)
    db.session.commit()
    flash("Influencer deleted successfully!", "success")
    return redirect(url_for("profiles_blueprint.influencers"))


@blueprint.route("/influencer_edit/<int:influencer_id>", methods=["GET", "POST"])
# @login_required
def influencer_edit(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("profiles_blueprint.influencers"))

    form = InfluencerForm(obj=influencer)  # Create an instance of the form
    if form.validate_on_submit():
                influencer.full_name=form.full_name.data
                influencer.gender=form.gender.data
                influencer.country=form.country.data
                influencer.city=form.city.data
                influencer.phone=form.phone.data
                influencer.email=form.email.data
                # influencer.profile_picture=form.profile_picture.data

                if type(form.profile_picture)==FileField and form.profile_picture.data:
                    influencer.save_profile_picture(form.profile_picture.data)

                db.session.commit()
                flash("Influencer updated successfully!", "success")
                return redirect(url_for("profiles_blueprint.influencers"))
    
    return render_template(
        "profiles/influencer_edit.html", form=form, influencer=influencer
    )
