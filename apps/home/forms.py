from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import Email, DataRequired
from flask_wtf.file import FileField, FileAllowed


class InfluencerForm(FlaskForm):
    full_name = StringField("الإسم بالكامل", validators=[DataRequired()])
    gender = SelectField(
        "الجنس",
        choices=[("ذكر", "ذكر"), ("أنثى", "أنثى"), ("أخرى", "أخرى")],
    )
    country = StringField("البلد")
    city = StringField("المدينة")
    phone = StringField("رقم الهاتف")
    email = StringField("البريد الإلكتروني", validators=[Email()])
    profile_picture = FileField("صورة الملف الرئيسية", validators=[FileAllowed(["jpg", "png"], "Images only!")])
    
    
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


