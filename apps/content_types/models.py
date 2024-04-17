from flask_login import current_user
from apps import db
from icecream import ic


# Define Influencers Model
class Content(db.Model):
    __tablename__ = "contents"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String)
    creation_date = db.Column(db.Date, nullable=True, default=db.func.current_date())
    creation_time = db.Column(db.Time, nullable=True, default=db.func.current_time())
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("Users.id"),
        nullable=True,
    )
    # socialaccounts = db.relationship("SocialAccount", secondary="socialaccount_content", backref="contents", lazy=True)

from sqlalchemy import event

@event.listens_for(Content, "before_insert")
def before_insert_listener(mapper, connection, target):
    if current_user.is_authenticated:
        target.created_by = current_user.id
