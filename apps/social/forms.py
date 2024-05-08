from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SelectField, ValidationError
from wtforms.validators import  DataRequired
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

from apps.content_types.models import Content

class SocialAccountForm(FlaskForm):
    platform = SelectField("المنصة",validators=[DataRequired()])
    username = StringField("إسم المستخدم", validators=[DataRequired()])
    # content_type = SelectField("نوع المحتوى",validators=[DataRequired()])
    bio_text = StringField("البايو")
    profile_picture = HiddenField("صورة الحساب")
    # contents = QuerySelectMultipleField(query_factory=lambda: Content.query.all())
    contents = QuerySelectMultipleField("المحتوى", query_factory=lambda: Content.query.all(), get_label="name", allow_blank=False, blank_text="إختر نوع المحتوى")
    external_url = StringField("الرابط الخارجي", render_kw={"readonly": True, "type": "url"})
    public_profile_name = StringField("الإسم على المنصة", render_kw={"readonly": True})
    # set_as_default_profile_picture = BooleanField("إستخدم صورة الحساب كصورة رئيسية للملف")

    def validate_contents(form, field):
        if not any(choice.data for choice in field):
            raise ValidationError("At least one checkbox must be checked.")
