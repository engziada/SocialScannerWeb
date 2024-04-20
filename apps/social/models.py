from flask_login import current_user
import requests
from apps import db
from werkzeug.utils import secure_filename
from os import path, makedirs
from flask import current_app
from icecream import ic
import datetime


class Platform(db.Model):
    __tablename__ = "platforms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
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


# Define Subprofiles Model
class SocialAccount(db.Model):
    __tablename__ = "socialaccounts"
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey("influencers.id"), nullable=False)
    # platform = db.Column(db.String, nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey("platforms.id"), nullable=False)
    platform = db.relationship("Platform", backref="socialaccounts", lazy=True)
    username = db.Column(db.String, nullable=False, unique=True)
    contents = db.relationship("Content", secondary="socialaccount_content", backref="socialaccounts", lazy=True)
    description = db.Column(db.Text)
    profile_picture = db.Column(db.String)
    scan_logs = db.relationship("ScanLog", backref="socialaccount", lazy=True)
    creation_date = db.Column(db.Date, nullable=True, default=db.func.current_date())
    creation_time = db.Column(db.Time, nullable=True, default=db.func.current_time())
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("Users.id"),
        nullable=True,
    )
    # scanlogs = db.relationship("ScanLog", back_populates="socialaccount")

    def __repr__(self):
        return f"SocialAccount(id={self.id}, platform='{self.platform}', username='{self.username}')"

    def save_profile_picture(self, picture_file):
        if picture_file:
            upload_folder = path.join(current_app.root_path, "static", "profile_pictures")
            if not path.exists(upload_folder):
                makedirs(upload_folder)
            filename = secure_filename(picture_file.filename)
            current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            new_filename = f'{current_time}.{filename.split(".")[-1]}'
            filepath = path.join(upload_folder, new_filename)
            picture_file.save(filepath)
            self.profile_picture = new_filename
            db.session.commit()

    def download_image(self, image_url):
        response = requests.get(image_url)
        upload_folder = path.join(current_app.root_path, "static", "profile_pictures")
        if not path.exists(upload_folder):
            makedirs(upload_folder)
        current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        new_filename = secure_filename(f"{current_time}.jpg")
        filepath = path.join(upload_folder, new_filename)
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
    


from sqlalchemy import event


@event.listens_for(SocialAccount, "before_insert")
@event.listens_for(Platform, "before_insert")
def before_insert_listener(mapper, connection, target):
    if current_user.is_authenticated:
        target.created_by = current_user.id
        
