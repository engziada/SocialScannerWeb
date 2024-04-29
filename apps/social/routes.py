import profile
from apps import db

from flask import render_template, redirect, request, session, url_for, flash
from flask_wtf.file import FileField

from apps.home.models import Log
from apps.home.util import search_user_profile
from apps.social import blueprint
from apps.social.forms import  SocialAccountForm
from apps.social.models import  SocialAccount, Platform
from apps.profiles.models import Influencer
from apps.content_types.models import Content

from icecream import ic
from sqlalchemy.exc import IntegrityError


@blueprint.route("/socialaccounts/<int:influencer_id>")
# @login_required
def socialaccounts(influencer_id):
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("الملف غير موجود", "danger")
        return redirect(url_for("social_blueprint.influencers"))

    socialaccounts = (
        SocialAccount.query.filter_by(influencer_id=influencer_id)
        .paginate(page=page, per_page=per_page)
        # .all()
    )  # Fetch social accounts for a specific influencer
    return render_template(
        "social/socialaccounts.html",
        socialaccounts=socialaccounts,
        influencer=influencer,
    )


@blueprint.route("/socialaccount_add/<int:influencer_id>", methods=["GET", "POST"])
# @login_required
@Log.add_log("إضافة حساب")
def socialaccount_add(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("الملف غير موجود", "danger")
        return redirect(url_for("social_blueprint.influencers"))

    profile_data = {}
    if session.get("profile_data"):
        profile_data = session["profile_data"]
        # session.pop("profile_data")
    else:
        return redirect(url_for("home_blueprint.search"))

    
    form = SocialAccountForm()  # Create an instance of the form
    # form.content_type.choices = [(content.id, content.name) for content in Content.query.all()]
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]
    form.platform.data = profile_data.get("platform_id") if profile_data.get("platform_id") else 1
    form.username.data = profile_data.get("username") if profile_data.get("username") else ""
    form.bio_text.data = profile_data.get("bio_text") if profile_data.get("bio_text") else "No Bio"
    form.profile_picture.data = profile_data.get("profile_picture") if profile_data.get("profile_picture") else None

    if form.validate_on_submit():
        try:
            new_socialaccount = SocialAccount(
                influencer_id=influencer_id,
                platform_id=form.platform.data,
                username=form.username.data,
                contents=Content.query.filter(Content.id.in_(request.form.getlist("contents"))).all(),
                bio_text=form.bio_text.data,
                profile_picture=None,  # Set a default value initially
                external_url=form.external_url.data,
                public_profile_name=form.public_profile_name.data,
            )

            # # Check if the profile picture is a URL/Local and save it
            # set_as_default_profile_picture = form.set_as_default_profile_picture.data if hasattr(form, 'set_as_default_profile_picture') else False
            # if profile_data and profile_data["profile_picture"] and set_as_default_profile_picture:
            #     new_socialaccount.download_image(profile_data["profile_picture"])
            ic(form.profile_picture.data, profile_data.get("profile_picture"))
            if form.profile_picture.data:
                new_socialaccount.download_image(form.profile_picture.data)

            db.session.add(new_socialaccount)
            db.session.commit()
            ic(new_socialaccount.id)
            flash("تم إضافة الحساب", "success")
            session.pop("profile_data")
            return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))
        except IntegrityError:
            ic("IntegrityError")
            db.session.rollback()
            flash("إسم الحساب موجود بالفعل", "danger")
        except Exception as e:
            ic(e)
            db.session.rollback()
            flash(f"حدث خطأ أثناء تسجيل البيانات\n{e}", "danger")
    else:
        # Form validation failed
        errors = form.errors
        ic(errors)
    return render_template("social/socialaccount_add.html", form=form, influencer=influencer, profile_data=profile_data)


@blueprint.route("/socialaccount_delete/<int:influencer_id>/<int:socialaccount_id>", methods=["POST"])
# @login_required
@Log.add_log("حذف حساب")
def socialaccount_delete(influencer_id, socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("الحساب غير موجود", "danger")
        return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))
    db.session.delete(socialaccount)
    db.session.commit()
    flash("تم حذف الحساب", "success")
    return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))


@blueprint.route("/socialaccount_edit/<int:influencer_id>/<int:socialaccount_id>",methods=["GET", "POST"])
# @login_required
@Log.add_log("تعديل حساب")
def socialaccount_edit(influencer_id, socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("الحساب غير موجود", "danger")
        return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))

    # Do search
    try:
        profile_data = search_user_profile(socialaccount.username, socialaccount.platform_id)
        if not profile_data:
            flash("لا يمكن العثور على الحساب", "danger")
        elif profile_data.get("error") is not None:
            flash(profile_data["error"], "danger")
        else:
            session["profile_data"] = profile_data
    except Exception as e:
        flash(f"Error: {str(e)}")  # Handle backend errors gracefully

    form = SocialAccountForm(obj=socialaccount)  # Create an instance of the form and populate it with existing data
    # form.content_type.choices = [(content.id, content.name) for content in Content.query.all()]
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]
    selected_platform = Platform.query.filter_by(id=socialaccount.platform_id).first()
    form.platform.data = selected_platform if selected_platform else 1
    ic(selected_platform, form.platform.data)
    form.external_url.data = (
        profile_data.get("external_url")
        if socialaccount.external_url == ""
        else socialaccount.external_url
    )
    form.public_profile_name.data = (
        profile_data.get("public_profile_name")
        if socialaccount.public_profile_name == ""
        else socialaccount.public_profile_name
    )
    form.process()

    if form.validate_on_submit():
        ic(form)
        socialaccount.platform_id = form.platform.data
        socialaccount.username = form.username.data
        socialaccount.contents = Content.query.filter(Content.id.in_(request.form.getlist("contents"))).all()
        socialaccount.bio_text = form.bio_text.data
        socialaccount.external_url = form.external_url.data
        socialaccount.public_profile_name = form.public_profile_name.data

        if type(form.profile_picture) == FileField and form.profile_picture.data:
            socialaccount.save_profile_picture(form.profile_picture.data)

        db.session.commit()
        flash("تم تعديل الحساب", "success")
        return redirect(
            url_for(
                "social_blueprint.socialaccounts",
                influencer_id=socialaccount.influencer_id,
            )
        )

    return render_template(
        "social/socialaccount_edit.html", form=form, socialaccount=socialaccount, influencer=socialaccount.influencer, profile_data=profile_data)

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////