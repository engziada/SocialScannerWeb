from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired

# login and registration


class LoginForm(FlaskForm):
    username = StringField('إسم المستخدم',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('كلمة المرور',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField('إسم المستخدم',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('البريد الالكتروني',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور',
                             id='pwd_create',
                             validators=[DataRequired()])
