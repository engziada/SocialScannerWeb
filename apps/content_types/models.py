from apps import db
from icecream import ic

# Define Influencers Model
class Content(db.Model):
    __tablename__ = "contents"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    # socialaccounts = db.relationship("SocialAccount", secondary="socialaccount_content", backref="contents", lazy=True)
    