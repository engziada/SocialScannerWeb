from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import  DataRequired

class SocialAccountForm(FlaskForm):
    platform = SelectField("المنصة",validators=[DataRequired()])
    username = StringField("إسم المستخدم", validators=[DataRequired()])
    content_type = SelectField("نوع المحتوى",validators=[DataRequired()])
    description = StringField("الوصف")
    profile_picture = StringField("صورة الحساب",render_kw={"readonly": True})


