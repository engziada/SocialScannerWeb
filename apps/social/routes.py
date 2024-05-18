from apps import db

from flask import render_template, redirect, request, session, url_for, flash
from flask_login import login_required

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
@login_required
def socialaccounts(influencer_id):
    """
    Retrieves a paginated list of social accounts associated with a specific influencer.

    Parameters:
        influencer_id (int): The ID of the influencer.

    Returns:
        flask.Response: The rendered template with the social accounts and influencer information.

    Raises:
        None
    """
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
@login_required
@Log.add_log("إضافة حساب")
def socialaccount_add(influencer_id):
    """
    A view function to add a social account for a specific influencer. Handles form submission, data validation, and database operations. Returns the rendered template with the form, influencer, and profile data.
    """
    referer = request.headers.get("Referer")
    if referer:
        # ic(f"This route was redirected from {referer}")
        if referer.endswith("influencers"):
            session.pop("profile_data", None)

    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        flash("الملف غير موجود", "danger")
        return redirect(url_for("social_blueprint.influencers"))

    profile_data = {}
    if session.get("profile_data"):
        profile_data = session["profile_data"]
        # session.pop("profile_data")
    else:
        session["current_influencer_id"] = influencer_id
        return redirect(url_for("home_blueprint.search"))

    
    form = SocialAccountForm()  # Create an instance of the form
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

            if form.profile_picture.data:
                new_socialaccount.download_image(form.profile_picture.data)

            db.session.add(new_socialaccount)
            db.session.commit()
            flash("تم إضافة الحساب", "success")
            session.pop("profile_data")
            return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))
        except IntegrityError as e:
            ic("IntegrityError in <SocialAccount_Add>:", e)
            db.session.rollback()
            flash("إسم الحساب موجود بالفعل", "danger")
        except Exception as e:
            ic("Error in <SocialAccount_Add>: ", e)
            db.session.rollback()
            flash(f"حدث خطأ أثناء تسجيل البيانات\n{e}", "danger")
    else:
        # Form validation failed
        errors = form.errors
        ic("SocialAccount_Add=>", errors)
    return render_template("social/socialaccount_add.html", form=form, influencer=influencer, profile_data=profile_data)


@blueprint.route("/socialaccount_delete/<int:influencer_id>/<int:socialaccount_id>", methods=["POST"])
@login_required
@Log.add_log("حذف حساب")
def socialaccount_delete(influencer_id, socialaccount_id):
    """
    A view function to delete a social account for a specific influencer. 
    Handles the POST request to delete a social account. 

    Args:
        influencer_id (int): The ID of the influencer.
        socialaccount_id (int): The ID of the social account to be deleted.

    Returns:
        redirect: Redirects to the social accounts page of the influencer after deleting the social account.
    """
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("الحساب غير موجود", "danger")
        return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))
    db.session.delete(socialaccount)
    db.session.commit()
    flash("تم حذف الحساب", "success")
    return redirect(url_for("social_blueprint.socialaccounts", influencer_id=influencer_id))


@blueprint.route("/socialaccount_edit/<int:socialaccount_id>",methods=["GET", "POST"])
@login_required
@Log.add_log("تعديل حساب")
def socialaccount_edit(socialaccount_id):
    """
    A view function to edit a social account for a specific influencer. 
    Handles the GET and POST requests to edit a social account. 

    Args:
        socialaccount_id (int): The ID of the social account to be edited.

    Returns:
        redirect or render_template: If the form is valid, redirects to the social accounts page of the influencer after editing the social account. 
        Otherwise, renders the socialaccount_edit.html template with the form and relevant data.
    """
    socialaccount = SocialAccount.query.get(socialaccount_id)
    if not socialaccount:
        flash("الحساب غير موجود", "danger")
        return redirect(url_for("profiles_blueprint.influencers"))

    # Do search
    profile_data = {}
    try:
        profile_data = search_user_profile(socialaccount.username, socialaccount.platform_id)
        if not profile_data:
            flash("لا يمكن العثور على الحساب", "danger")
        elif profile_data.get("error") is not None:
            flash(profile_data["error"], "danger")
        else:
            session["profile_data"] = profile_data
    except Exception as e:
        ic("Error in <SocialAccount_Edit>: ", e)
        flash(f"Error: {str(e)}")  # Handle backend errors gracefully

    form = SocialAccountForm()  # Create an instance of the form and populate it with existing data
    
    # Get all platforms from the database
    choices = [(platform.id, platform.name) for platform in Platform.query.all()]
    selected_choice = next((choice for choice in choices if choice[0] == socialaccount.platform_id), None)
    if selected_choice:
        choices.remove(selected_choice)
        choices.insert(0, selected_choice)
    form.platform.choices = choices
    # form.platform.data = str(socialaccount.platform_id)  # Assuming platform is a foreign key
    form.username.data = socialaccount.username
    form.contents.data = socialaccount.contents
    # Set the data for the bio_text field
    if socialaccount.bio_text:
        form.bio_text.data = socialaccount.bio_text
        form.is_edited = False  # The form has not been edited
    else:
        form.bio_text.data = profile_data.get("bio_text") if profile_data else "No Bio"
        form.is_edited = True
    # Set the data for the external_url field
    if socialaccount.external_url:
        form.external_url.data = socialaccount.external_url
        form.is_edited = False  # The form has not been edited
    else:
        form.external_url.data = profile_data.get("external_url") if profile_data else ""
        form.is_edited = True      
    # Set the data for the public_profile_name field
    if socialaccount.public_profile_name:
        form.public_profile_name.data = socialaccount.public_profile_name
        form.is_edited = False  # The form has not been edited
    else:
        form.public_profile_name.data = profile_data.get("public_profile_name") if profile_data else ""
        form.is_edited = True  
    # Set the data for the profile_picture field
    if socialaccount.profile_picture:
        form.profile_picture.data = socialaccount.profile_picture
        form.is_edited = False  # The form has not been edited
    else:
        socialaccount.download_image(profile_data.get("profile_picture")) if profile_data else None
        form.is_edited = True 
        
    if form.validate_on_submit():
        socialaccount.platform_id = form.platform.data
        socialaccount.username = form.username.data
        socialaccount.contents = Content.query.filter(Content.id.in_(request.form.getlist("contents"))).all()
        socialaccount.bio_text = form.bio_text.data
        socialaccount.external_url = form.external_url.data
        socialaccount.public_profile_name = form.public_profile_name.data

        # if type(form.profile_picture) == FileField and form.profile_picture.data:
        #     socialaccount.save_profile_picture(form.profile_picture.data)

        db.session.commit()
        session.pop("profile_data")
        flash("تم تعديل الحساب", "success")
        return redirect(url_for("social_blueprint.socialaccounts",influencer_id=socialaccount.influencer_id,)
        )
    else:
        errors = form.errors
        ic("SocialAccount_Edit=>", errors)

    return render_template("social/socialaccount_edit.html", form=form, socialaccount=socialaccount, influencer=socialaccount.influencer, profile_data=profile_data)
