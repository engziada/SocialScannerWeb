from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import  DataRequired
    
class SocialAccountForm(FlaskForm):
    platform = SelectField(
        "المنصة",
        choices=[
            ("سناب شات", "سناب شات"),
            ("تيك توك", "تيك توك"),
            ("إنستاغرام", "إنستاغرام"),
            ("أخرى", "أخرى"),
        ],
        validators=[DataRequired()],
    )
    username = StringField("إسم المستخدم", validators=[DataRequired()])
    content_type = StringField("نوع المحتوى")
    description = StringField("الوصف")
    profile_picture = StringField("صورة الحساب",render_kw={"readonly": True})


