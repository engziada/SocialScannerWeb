from apps import db

from flask import (
    jsonify,
    render_template,
    redirect,
    request,
    session,
    url_for,
    flash,
)
from flask_wtf.file import FileField
from sqlalchemy import desc
from icecream import ic
from sqlalchemy.exc import IntegrityError

from apps.home.models import Log
from apps.home.util import search_user_profile
from apps.profiles import blueprint
from apps.profiles.forms import InfluencerForm
from apps.profiles.models import Influencer

from apps.reports.models import ScanResults
from apps.social.models import SocialAccount


@blueprint.route("/influencers")
# @login_required
def influencers():
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    # Get search term from query string (optional)
    search_terms = request.args.get("q", "")

    # filter influencers
    influencers = (
        Influencer.query.filter(
            (Influencer.full_name.ilike(f"%{search_terms}%"))
            | (
                Influencer.socialaccounts.any(
                    SocialAccount.username.ilike(f"%{search_terms}%")
                )
            )
        )
        .paginate(page=page, per_page=per_page)
        # .all()
    )
    return render_template("profiles/influencers.html", influencers=influencers)


@blueprint.route("/influencer_add", methods=["GET", "POST"])
# @login_required
@Log.add_log("إضافة ملف")
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
                new_influencer.save_profile_picture(picture_file=form.profile_picture.data)

            db.session.add(new_influencer)
            db.session.commit()
            flash("تم إضافة الملف", "success")
            return redirect(url_for("social_blueprint.socialaccount_add",influencer_id=new_influencer.id,profile_data=profile_data,))
        except IntegrityError:
            db.session.rollback()
            flash(
                "إسم الملف موجود بالفعل, تم تحويلك إلى صفحة تعديل الملف",
                "danger",
            )
            influencer_id = (
                Influencer.query.filter_by(full_name=form.full_name.data).first().id
            )
            # return redirect(url_for("social_blueprint.socialaccount_add",influencer_id=influencer_id,profile_data=profile_data,))
            return redirect(
                url_for(
                    "profiles_blueprint.influencer_edit",
                    influencer_id=influencer_id,
                    profile_data=profile_data,
                )
            )

        except Exception as e:
            db.session.rollback()
            flash(f"حدث خطأ أثناء إضافة الملف\n{e}", "danger")
    return render_template("profiles/influencer_add.html", form=form, profile_data=profile_data)


@blueprint.route("/influencer_delete/<int:influencer_id>", methods=["POST"])
# @login_required
@Log.add_log("حذف ملف")
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
@Log.add_log("تعديل ملف")
def influencer_edit(influencer_id):
    # profile_data = {}
    # if session.get("profile_data"):
    #     profile_data = session["profile_data"]
    #     # session.pop("profile_data")

    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("الملف غير موجود", "danger")
        return redirect(url_for("profiles_blueprint.influencers"))

    # Prepare the data for the template
    scanresults=[]
    socialaccounts = influencer.socialaccounts
    for socialaccount in socialaccounts:
        scan_result = (
            db.session.query(ScanResults)
            .filter_by(socialaccount_id=socialaccount.id)
            .order_by(desc(ScanResults.creation_date))
            .limit(5)
            .all()
        )
        scanresults.extend(scan_result)

    profile_data_list = []
    for socialaccount in socialaccounts:
        profile_data = search_user_profile(socialaccount.username, socialaccount.platform_id)
        profile_data_list.append(profile_data)

    form = InfluencerForm(obj=influencer)  # Create an instance of the form
    if form.validate_on_submit():
        influencer.full_name = form.full_name.data
        influencer.gender = form.gender.data
        influencer.country = form.country.data
        influencer.city = form.city.data
        influencer.phone = form.phone.data
        influencer.email = form.email.data
        # influencer.profile_picture=form.profile_picture.data
        
        ic(form.profile_picture.data)
        if type(form.profile_picture) == FileField and form.profile_picture.data:
            influencer.save_profile_picture(picture_file=form.profile_picture.data)

        db.session.commit()
        flash("تم تعديل الملف", "success")
        return redirect(url_for("profiles_blueprint.influencers"))

    return render_template(
        "profiles/influencer_edit.html",
        form=form,
        influencer=influencer,
        scanresults=scanresults,
        profile_data_list=profile_data_list,
    )
    
    
@blueprint.route("/influencer/update_picture", methods=["POST"])
# @login_required
@Log.add_log("تعديل صورة ملف")
def influencer_update_picture():
    influencer_id = request.form.get('influencer_id')
    picture_url = request.form.get('picture_url')
    # get influencer
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("الملف غير موجود", "danger")
        return jsonify({"redirect_url": url_for("profiles_blueprint.influencers")})
    influencer.download_image(picture_url)
    flash("تم تعديل الصورة", "success")
    return jsonify(
        {
            "redirect_url": url_for(
                "profiles_blueprint.influencer_edit", influencer_id=influencer_id
            )
        }
    )