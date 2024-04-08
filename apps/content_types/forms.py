from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ContentForm(FlaskForm):
    name = StringField("المحتوى", validators=[DataRequired()])
    description = StringField("الوصف")
    
