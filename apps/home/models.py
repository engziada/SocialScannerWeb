from apps import db
# from apps.home.util import *
from werkzeug.utils import secure_filename
from os import path, makedirs
from flask import current_app
from icecream import ic
import datetime

# Define Influencers Model
class Influencer(db.Model):
    __tablename__ = "influencers"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String)
    country = db.Column(db.String)
    city = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)
    profile_picture = db.Column(db.String)
    socialaccounts = db.relationship("SocialAccount", backref="influencer", lazy=True)
    
    def __repr__(self):
        return f"Influencer(id={self.id}, full_name='{self.full_name}'), email='{self.email}', phone='{self.phone}', country='{self.country}', city='{self.city}', profile_picture='{self.profile_picture}', socialaccounts='{self.socialaccounts}'"

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

# Define Subprofiles Model
class SocialAccount(db.Model):
    __tablename__ = "socialaccounts"
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey("influencers.id"), nullable=False)
    platform = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    content_type = db.Column(db.String)
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


# Define ScanLogs Model
class ScanLog(db.Model):
    __tablename__ = "scanlogs"
    id = db.Column(db.Integer, primary_key=True)
    socialaccount_id = db.Column(db.Integer, db.ForeignKey("socialaccounts.id"), nullable=False)
    scan_date = db.Column(db.Date)
    scan_time = db.Column(db.Time)
    public_profile_name = db.Column(db.String)
    bio_text = db.Column(db.Text)
    profile_picture = db.Column(db.String)
    followers = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    posts = db.Column(db.Integer)
  
    def __repr__(self):
        return f"ScanLog(id={self.id}, scan_date='{self.scan_date}', platform='{self.socialaccount.platform}')"
    
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