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
    content_id = db.Column(db.Integer, db.ForeignKey("contents.id"), nullable=False)
    content = db.relationship("Content", backref="socialaccount", lazy=True)
    description = db.Column(db.Text)
    profile_picture = db.Column(db.String)
    scan_logs = db.relationship("ScanLog", backref="socialaccount", lazy=True)
    
    def __repr__(self):
        return f"SocialAccount(id={self.id}, platform='{self.platform}', username='{self.username}')"

    def save_profile_picture(self, picture_file):
        if picture_file:
            upload_folder = path.join(
                current_app.root_path, "static", "profile_pictures"
            )
            if not path.exists(upload_folder):
                makedirs(upload_folder)
            filename = secure_filename(picture_file.filename)
            current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            new_filename = f'{current_time}.{filename.split(".")[-1]}'
            filepath = path.join(upload_folder, new_filename)
            picture_file.save(filepath)
            self.profile_picture = new_filename
            db.session.commit()