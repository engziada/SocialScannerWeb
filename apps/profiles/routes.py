from flask import (
    render_template,
    redirect,
    request,
    session,
    url_for,
    flash,
)
from flask_wtf.file import FileField

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
                new_influencer.upload_profile_picture(form.profile_picture.data)

            db.session.add(new_influencer)
            db.session.commit()
            flash("Influencer created successfully!", "success")
            return redirect(url_for("social_blueprint.socialaccount_add",influencer_id=new_influencer.id,profile_data=profile_data,))
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists!", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating the Profile!\n{e}", "danger")
    return render_template("profiles/influencer_add.html", form=form, profile_data=profile_data)


@blueprint.route("/influencer_delete/<int:influencer_id>", methods=["POST"])
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
        flash("Influencer updated successfully!", "success")
        return redirect(url_for("profiles_blueprint.influencers"))

    return render_template(
        "profiles/influencer_edit.html", form=form, influencer=influencer
    )


# @blueprint.route("/download_image", methods=["POST"])
# def download_image():
#     image_url = request.form.get("profile_picture")  # Check for hidden field

#     response = requests.get(image_url)

#     upload_folder = path.join(current_app.root_path, "static", "profile_pictures")
#     if not path.exists(upload_folder):
#         makedirs(upload_folder)

#     # filename = secure_filename(picture_file.filename)
#     current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
#     new_filename = secure_filename(f"{current_time}.jpg")
#     filepath = path.join(upload_folder, new_filename)

#     with open(filepath, "wb") as f:
#         f.write(response.content)

#     # Here you would update your form or database with the new local path
#     # This depends on how your application is structured

#     return redirect(request.referrer + "?filepath=" + filepath)


# def save_profile_picture(self, picture_file):
#     if picture_file:
#         if picture_file.startswith("http"):
#             response = requests.get(picture_file)
#             if response.status_code == 200:
#                 picture_data = response.content
#                 picture_stream = BytesIO(picture_data)
#                 filename = picture_file.split("/")[-1]
#             else:
#                 raise ValueError("Failed to download image from URL")
#         else:
#             filename = secure_filename(picture_file.filename)
#             picture_stream = picture_file.stream

#         upload_folder = path.join(
#             current_app.root_path, "static", "profile_pictures"
#         )
#         if not path.exists(upload_folder):
#             makedirs(upload_folder)

#         current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
#         new_filename = f'{current_time}.{filename.split(".")[-1]}'
#         filepath = path.join(upload_folder, new_filename)

#         with open(filepath, "wb") as f:
#             f.write(picture_stream.read())

#         self.profile_picture = new_filename
#         db.session.commit()
