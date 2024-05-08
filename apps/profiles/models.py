from flask_login import current_user
import requests
from apps import db
from werkzeug.utils import secure_filename
from os import path, makedirs
from flask import current_app, request
from icecream import ic
import datetime
from sqlalchemy import event


# Define Influencers Model
class Influencer(db.Model):
    __tablename__ = "influencers"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String, nullable=False, unique=True)
    gender = db.Column(db.String)
    country = db.Column(db.String)
    city = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String,)
    profile_picture = db.Column(db.String)
    socialaccounts = db.relationship("SocialAccount", backref="influencer", lazy=True, cascade="all, delete-orphan")
    creation_date = db.Column(db.Date, nullable=True, default=db.func.current_date())
    creation_time = db.Column(db.Time, nullable=True, default=db.func.current_time())
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("Users.id"),
        nullable=True,
    )

    def __repr__(self):
        return f"Influencer(id={self.id}, full_name='{self.full_name}'), email='{self.email}', phone='{self.phone}', country='{self.country}', city='{self.city}', profile_picture='{self.profile_picture}', socialaccounts='{self.socialaccounts}'"

    def save_profile_picture(self, picture_file):
        """
        Saves the profile picture provided as 'picture_file' in the static folder.
        
        Args:
            picture_file: The file object representing the profile picture to be saved.
        
        Returns:
            None
        """
        upload_folder = path.join(current_app.root_path, "static", "profile_pictures")
        if not path.exists(upload_folder):
            makedirs(upload_folder)
        current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        if picture_file:
            if path.exists(path.join(upload_folder, picture_file)):
                return
            filename = secure_filename(picture_file.filename)
            new_filename = f'{current_time}.{filename.split(".")[-1]}'
            filepath = path.join(upload_folder, new_filename)
            picture_file.save(filepath)
            self.profile_picture = new_filename
            db.session.commit()


    def download_image(self, image_url):
        """
        Downloads an image from the specified URL, saves it in the static folder, and updates the profile_picture attribute of the object.
        
        Parameters:
            self: The instance of the class.
            image_url (str): The URL of the image to download.
        
        Returns:
            None
        """
        if image_url.startswith("/static"):
            scheme = request.scheme  # http or https
            server_name = request.host  # localhost:5000
            image_url = f"{scheme}://{server_name}{image_url}"

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


@event.listens_for(Influencer, "before_insert")
def before_insert_listener(mapper, connection, target):
    """
    Listens for the "before_insert" event on the Influencer model and sets the "created_by" attribute of the target object to the id of the currently authenticated user.
    """
    if current_user.is_authenticated:
        target.created_by = current_user.id
