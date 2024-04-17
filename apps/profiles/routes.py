from flask import (
    render_template,
    redirect,
    request,
    session,
    url_for,
    flash,
)
from flask_wtf.file import FileField

from apps.home.models import Log
from apps.profiles import blueprint

from apps import db

from apps.profiles.forms import InfluencerForm
from apps.profiles.models import Influencer

from icecream import ic
from sqlalchemy.exc import IntegrityError


@blueprint.route("/influencers")
# @login_required
def influencers():
    # Get search term from query string (optional)
    search_term = request.args.get("q", "")
    # Fetch all influencers
    influencers = Influencer.query.all()
    if search_term:
        # Filter based on search term (name)
        influencers = [
            influencer
            for influencer in influencers
            if search_term.lower() in influencer.full_name.lower()
        ]
    return render_template("profiles/influencers.html", influencers=influencers)


@blueprint.route("/influencer_add", methods=["GET", "POST"])
# @login_required
@Log.add_log_early("إضافة ملف")
def influencer_add():
    profile_data = {}
    if session.get("profile_data"):
        profile_data = session["profile_data"]
        # session.pop("profile_data")

    form = InfluencerForm()  # Create an instance of the form
    if form.validate_on_submit():
        try:
            new_influencer = Influencer(
                full_name=form.full_name.data,
                gender=form.gender.data,
                country=form.country.data,
                city=form.city.data,
                phone=form.phone.data,
                email=form.email.data,
                profile_picture=None,  # Set a default value initially
            )

            # Check if the profile picture is a URL/Local and save it
            set_as_default_profile_picture = form.set_as_default_profile_picture.data
            if profile_data and profile_data["profile_picture"] and set_as_default_profile_picture:
                new_influencer.download_image(profile_data["profile_picture"])
            elif form.profile_picture.data:
                new_influencer.save_profile_picture(form.profile_picture.data)

            db.session.add(new_influencer)
            db.session.commit()
            flash("تم إضافة الملف", "success")
            return redirect(url_for("social_blueprint.socialaccount_add",influencer_id=new_influencer.id,profile_data=profile_data,))
        except IntegrityError:
            db.session.rollback()
            flash("إسم الملف موجود بالفعل", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء إضافة الملف\n{e}", "danger")
    return render_template("profiles/influencer_add.html", form=form, profile_data=profile_data)


@blueprint.route("/influencer_delete/<int:influencer_id>", methods=["POST"])
# @login_required
@Log.add_log_early("حذف ملف")
def influencer_delete(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("الملف غير موجود", "danger")
        return redirect(url_for("profiles_blueprint.influencers"))
    db.session.delete(influencer)
    db.session.commit()
    flash("تم حذف الملف", "success")
    return redirect(url_for("profiles_blueprint.influencers"))


@blueprint.route("/influencer_edit/<int:influencer_id>", methods=["GET", "POST"])
# @login_required
@Log.add_log_early("تعديل ملف")
def influencer_edit(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("الملف غير موجود", "danger")
        return redirect(url_for("profiles_blueprint.influencers"))

    form = InfluencerForm(obj=influencer)  # Create an instance of the form
    if form.validate_on_submit():
        influencer.full_name = form.full_name.data
        influencer.gender = form.gender.data
        influencer.country = form.country.data
        influencer.city = form.city.data
        influencer.phone = form.phone.data
        influencer.email = form.email.data
        # influencer.profile_picture=form.profile_picture.data
        
        if type(form.profile_picture) == FileField and form.profile_picture.data:
            influencer.save_profile_picture(form.profile_picture.data)

        db.session.commit()
        flash("تم تعديل الملف", "success")
        return redirect(url_for("profiles_blueprint.influencers"))

    return render_template(
        "profiles/influencer_edit.html", form=form, influencer=influencer
    )