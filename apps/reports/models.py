from apps import db
from werkzeug.utils import secure_filename
from os import path, makedirs
from flask import current_app
from icecream import ic
import datetime
from sqlalchemy.dialects.postgresql import JSONB


# Define ScanLogs Model
class ScanResults(db.Model):
    __tablename__ = "scanresults"
    id = db.Column(db.Integer, primary_key=True)
    socialaccount_id = db.Column(db.Integer, db.ForeignKey("socialaccounts.id"), nullable=False)
    socialaccount = db.relationship("SocialAccount", back_populates="scan_results")
    public_profile_name = db.Column(db.String(100))
    bio_text = db.Column(db.Text)
    external_url = db.Column(db.String(255))
    profile_picture = db.Column(db.String(255))
    followers = db.Column(db.Integer)
    likes = db.Column(db.Integer)
    posts = db.Column(db.Integer)
    creation_date = db.Column(db.Date, nullable=True, default=db.func.current_date())
    creation_time = db.Column(db.Time, nullable=True, default=db.func.current_time())
    time_taken = db.Column(db.String(20))

    def __repr__(self):
        return f"ScanResults(id={self.id}, scan_date='{self.scan_date}', platform='{self.socialaccount.platform}')"
    
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


class ScanLog(db.Model):
    __tablename__ = "scanlog"
    id = db.Column(db.Integer, primary_key=True)
    success_count = db.Column(JSONB)
    failure_count = db.Column(JSONB)
    failures = db.Column(JSONB)
    creation_date = db.Column(db.Date, nullable=True, default=db.func.current_date())
    creation_time = db.Column(db.Time, nullable=True, default=db.func.current_time())
    time_taken = db.Column(db.String(20))
