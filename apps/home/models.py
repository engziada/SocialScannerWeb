from apps import db
# from apps.home.util import *
from icecream import ic
import datetime


# The `Log` class represents a database table for storing logs with attributes such as user ID, log
# date, log time, and log text, and provides a method `add_log` to add new log entries to the
# database.
class Log(db.Model):
    __tablename__ = "log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    user = db.relationship("Users", backref="log", lazy=True)
    log_date = db.Column(db.Date)
    log_time = db.Column(db.Time)
    log_text = db.Column(db.String(255))
    

    """
    Add a log for the given user_id and log_text to the database.
    
    Args:
        self: the object itself
        user_id (int): the ID of the user
        log_text (str): the text of the log
        
    Returns:
        None
    """
    def add_log(self, user_id: int, log_text: str) -> None:
        if log_text:
            new_log = Log(
                user_id=user_id,
                log_date=datetime.datetime.now().date(),
                log_time=datetime.datetime.now().time(),
                log_text=log_text,
            )
            db.session.add(new_log)
            db.session.commit()

