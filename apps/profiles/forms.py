from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField
from wtforms.validators import Email, DataRequired, Optional
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
    email = StringField("البريد الإلكتروني", validators=[Optional(), Email()])
    profile_picture = FileField("صورة الملف الرئيسية", validators=[FileAllowed(["jpg", "png"], "Images only!")])
    set_as_default_profile_picture = BooleanField("إستخدم صورة الحساب كصورة رئيسية للملف")
    
