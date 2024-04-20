from flask import render_template, redirect, request, session, url_for, flash
from flask_wtf.file import FileField

from apps.home.models import Log
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
        flash("الملف غير موجود", "danger")
        return redirect(url_for("social_blueprint.influencers"))

    socialaccounts = SocialAccount.query.filter_by(influencer_id=influencer_id).all()  # Fetch social accounts for a specific influencer
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
    
    form = SocialAccountForm()  # Create an instance of the form
    # form.content_type.choices = [(content.id, content.name) for content in Content.query.all()]
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]

    if form.validate_on_submit():
        try:
            new_socialaccount = SocialAccount(
                influencer_id=influencer_id,
                platform_id=form.platform.data,
                username=form.username.data,
                contents=Content.query.filter(Content.id.in_(request.form.getlist('contents'))).all(),
                # form.contents.data,
                description=form.description.data,
                profile_picture=None,  # Set a default value initially
            )

            # Check if the profile picture is a URL/Local and save it
            set_as_default_profile_picture = form.set_as_default_profile_picture.data if hasattr(form, 'set_as_default_profile_picture') else False
            if profile_data and profile_data["profile_picture"] and set_as_default_profile_picture:
                new_socialaccount.download_image(profile_data["profile_picture"])
            elif form.profile_picture.data:
                new_socialaccount.save_profile_picture(form.profile_picture.data)

            db.session.add(new_socialaccount)
            db.session.commit()
            ic(new_socialaccount.id)
            flash("تم إضافة الحساب", "success")
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


@blueprint.route(
    "/socialaccount_edit/<int:influencer_id>/<int:socialaccount_id>",methods=["GET", "POST"],
)
# @login_required
@Log.add_log("تعديل حساب")
def socialaccount_edit(influencer_id, socialaccount_id):
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("الحساب غير موجود", "danger")
        return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))

    form = SocialAccountForm(obj=socialaccount)  # Create an instance of the form and populate it with existing data
    # form.content_type.choices = [(content.id, content.name) for content in Content.query.all()]
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]

    if form.validate_on_submit():
        socialaccount.platform_id = form.platform.data
        socialaccount.username = form.username.data
        socialaccount.contents = Content.query.filter(Content.id.in_(request.form.getlist("contents"))).all()
        # form.contents.data
        socialaccount.description = form.description.data

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
        "social/socialaccount_edit.html", form=form, socialaccount=socialaccount, influencer=socialaccount.influencer
    )

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////