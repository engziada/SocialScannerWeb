from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import  DataRequired
from wtforms_sqlalchemy.fields import QuerySelectMultipleField

from apps.content_types.models import Content

class SocialAccountForm(FlaskForm):
    platform = SelectField("المنصة",validators=[DataRequired()])
    username = StringField("إسم المستخدم", validators=[DataRequired()])
    # content_type = SelectField("نوع المحتوى",validators=[DataRequired()])
    description = StringField("الوصف")
    profile_picture = StringField("صورة الحساب",render_kw={"readonly": True})
    # contents = QuerySelectMultipleField(query_factory=lambda: Content.query.all())
    contents = QuerySelectMultipleField("المحتوى", query_factory=lambda: Content.query.all(), get_label="name",
                                        allow_blank=False, blank_text="Select a content type", validators=[DataRequired()])
