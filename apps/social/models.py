import os
import shutil
from flask_login import current_user
import requests
from apps import db
from werkzeug.utils import secure_filename
from os import path, makedirs
from flask import current_app, request
from icecream import ic
import datetime
from sqlalchemy import event


class Platform(db.Model):
    __tablename__ = "platforms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    name_english = db.Column(db.String(255), nullable=False, unique=True)
    # social_accounts = db.relationship("SocialAccount", backref="platform", lazy=True)
    creation_date = db.Column(db.Date, nullable=True, default=db.func.current_date())
    creation_time = db.Column(db.Time, nullable=True, default=db.func.current_time())
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("Users.id"),
        nullable=True,
    )

    def __repr__(self):
        return f"Platform(id={self.id}, name='{self.name}')"

# profile_data: dict = {
#     "followers": 0,
#     "likes": 0,
#     "posts": 0,
# }


# Define Subprofiles Model
class SocialAccount(db.Model):
    __tablename__ = "socialaccounts"
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey("influencers.id"), nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey("platforms.id"), nullable=False)
    platform = db.relationship("Platform", backref="socialaccounts", lazy=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    contents = db.relationship("Content", secondary="socialaccount_content", backref="socialaccounts", lazy=True)
    bio_text = db.Column(db.Text)
    profile_picture = db.Column(db.Text)
    public_profile_name = db.Column(db.String(100))
    external_url = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    posts = db.Column(db.Integer)
    scan_results = db.relationship("ScanResults", lazy=True, cascade="all, delete-orphan")
    creation_date = db.Column(db.Date, nullable=True, default=db.func.current_date())
    creation_time = db.Column(db.Time, nullable=True, default=db.func.current_time())
    created_by = db.Column(db.Integer,db.ForeignKey("Users.id"),nullable=True,)
    # scanlogs = db.relationship("ScanLog", back_populates="socialaccount")

    def __repr__(self):
        return f"SocialAccount(id={self.id}, platform='{self.platform}', username='{self.username}')"

    def save_profile_picture(self, picture_file):
        upload_folder = path.join(current_app.root_path, "static", "profile_pictures")
        if not path.exists(upload_folder):
            makedirs(upload_folder)
        current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        if picture_file:
            filename = secure_filename(picture_file.filename)
            new_filename = f'{current_time}.{filename.split(".")[-1]}'
            filepath = path.join(upload_folder, new_filename)
            picture_file.save(filepath)
            self.profile_picture = new_filename
            db.session.commit()

    def download_image(self, image_url):
        if not image_url:
            return
        
        upload_folder = path.join(current_app.root_path, "static", "profile_pictures")
        if not path.exists(upload_folder):
            makedirs(upload_folder)
        current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        new_filename = secure_filename(f"{current_time}.jpg")
        filepath = path.join(upload_folder, new_filename)

        if image_url.startswith("/static"):
            root_dir = os.path.dirname(os.path.abspath(__file__))
            # ic(root_dir)
            source_path = os.path.join(root_dir, upload_folder, "temp_insta_profile_image.jpg")
            # ic(source_path)
            destination_path = os.path.join(root_dir, upload_folder, new_filename)
            # ic(destination_path)
            shutil.copyfile(source_path, destination_path)
        else:
            response = requests.get(image_url)
            with open(filepath, "wb") as f:
                f.write(response.content)
        self.profile_picture = new_filename
        db.session.commit()


class SocialAccount_Content(db.Model):
    __tablename__ = "socialaccount_content"
    socialaccount_id = db.Column(db.Integer, db.ForeignKey("socialaccounts.id"), primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("contents.id"), primary_key=True)
    
    def __repr__(self):
        return f"SocialAccount_Content(socialaccount_id={self.socialaccount_id}, content_id={self.content_id})"
    


@event.listens_for(SocialAccount, "before_insert")
@event.listens_for(Platform, "before_insert")
def before_insert_listener(mapper, connection, target):
    if current_user.is_authenticated:
        target.created_by = current_user.id
        
