from flask import render_template, redirect, url_for, flash
from flask_wtf.file import FileField

from apps.social import blueprint

from apps import db

from apps.social.forms import  SocialAccountForm
from apps.social.models import  SocialAccount, Platform

from apps.profiles.models import Influencer
from apps.content_types.models import Content

from icecream import ic
from sqlalchemy.exc import IntegrityError


@blueprint.route("/socialaccounts/<int:influencer_id>")
# @login_required
def socialaccounts(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("social_blueprint.influencers"))

    socialaccounts = SocialAccount.query.filter_by(influencer_id=influencer_id).all()  # Fetch social accounts for a specific influencer
    return render_template(
        "social/socialaccounts.html",
        socialaccounts=socialaccounts,
        influencer=influencer,
    )


@blueprint.route("/socialaccount_add/<int:influencer_id>", methods=["GET", "POST"])
# @login_required
def socialaccount_add(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("Influencer not found!", "danger")
        return redirect(url_for("social_blueprint.influencers"))
    
    form = SocialAccountForm()  # Create an instance of the form
    form.content_type.choices = [(content.id, content.name) for content in Content.query.all()]
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]

    if form.validate_on_submit():
        try:
            new_socialaccount = SocialAccount(
                influencer_id=influencer_id,
                platform_id=form.platform.data,
                username=form.username.data,
                content_id=form.content_type.data,
                description=form.description.data,
                profile_picture=None,  # Set a default value initially
            )

            if form.profile_picture.data:
                new_socialaccount.save_profile_picture(form.profile_picture.data)

            db.session.add(new_socialaccount)
            db.session.commit()
            flash("Social Account created successfully!", "success")
            return redirect(
                url_for("social_blueprint.socialaccounts", influencer_id=influencer_id)
            )
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists!", "danger")
    return render_template("social/socialaccount_add.html", form=form, influencer=influencer)


@blueprint.route("/socialaccount_delete/<int:influencer_id>/<int:socialaccount_id>", methods=["POST"])
# @login_required
def socialaccount_delete(influencer_id, socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("Social Account not found!", "danger")
        return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))
    db.session.delete(socialaccount)
    db.session.commit()
    flash("Social Account deleted successfully!", "success")
    return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))


@blueprint.route(
    "/socialaccount_edit/<int:influencer_id>/<int:socialaccount_id>",methods=["GET", "POST"],
)
# @login_required
def socialaccount_edit(influencer_id, socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("Social Account not found!", "danger")
        return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))

    form = SocialAccountForm(obj=socialaccount)  # Create an instance of the form and populate it with existing data
    form.content_type.choices = [(content.id, content.name) for content in Content.query.all()]
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]

    if form.validate_on_submit():
        socialaccount.platform = form.platform.data
        socialaccount.username = form.username.data
        socialaccount.content_type = form.content_type.data
        socialaccount.description = form.description.data

        if type(form.profile_picture) == FileField and form.profile_picture.data:
            socialaccount.save_profile_picture(form.profile_picture.data)

        db.session.commit()
        flash("Social Account updated successfully!", "success")
        return redirect(
            url_for(
                "social_blueprint.socialaccounts",
                influencer_id=socialaccount.influencer_id,
            )
        )

    return render_template(
        "social/socialaccount_edit.html", form=form, socialaccount=socialaccount, influencer=socialaccount.influencer
    )

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////