from flask import flash, render_template, redirect, request, session, url_for, send_file
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint

from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users

from apps.authentication.util import verify_pass,create_default_admin

from apps.home.models import Log
from icecream import ic

from PostgreRenderCert import generate_certificate  # Import your existing function

@blueprint.route('/')
def route_default():
    """
    A route function that redirects to the login page.
    """
    # ic(session.get("original_url", url_for("authentication_blueprint.login")))
    original_url=session.pop("original_url", url_for("authentication_blueprint.login")) 
    return redirect(original_url)
    # return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
@Log.add_log("تسجيل دخول")  # Pass the message as an argument
def login():
    """
    A route function that handles the login process. It checks if the admin user exists and creates it if not. It then reads the form data, locates the user, and checks the password. If the user and password are valid, the user is logged in and redirected to the default route. If the user or password is incorrect, it renders the login template with an error message. If the user is not authenticated, it renders the login template. 
    """
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # Check if admin user exists, if not create it
        create_default_admin(Users=Users,db=db)
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg=' بيانات الحساب خطأ, من فضلك تأكد من إسم المستخدم و كلمة المرور',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
@Log.add_log("إضافة مستخدم")
@login_required
def register():
    """
    A route function that handles the user registration process. It creates an account form and checks if the username and email provided already exist in the database. If the username or email already exist, it renders the registration page with an error message. If the username and email are unique, it creates a new user, adds it to the database, and renders the registration success page. 
    """
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='إسم المستخدم موجود بالفعل',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='البريد الإلكتروني موجود بالفعل',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='تم إضافة الحساب,  <a href="/login">تسجيل دخول</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
@Log.add_log_early("تسجيل خروج")
def logout():
    """
    Logs out the current user and redirects them to the login page.

    This function is a route handler for the '/logout' endpoint. It is responsible for logging out the current user and redirecting them to the login page.

    Returns:
        flask.Response: A redirect response to the login page.
    """
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.route('/users', methods=['GET'])
@Log.add_log("عرض جميع المستخدمين")
@login_required
def users():
    users = Users.query.all()  # Assuming User is your user model
    return render_template('accounts/users.html', users=users)


@blueprint.route('/delete_user/<int:user_id>', methods=['POST'])
@Log.add_log("حذف المستخدم")
@login_required
def delete_user(user_id):
    user = Users.query.get(user_id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for("authentication_blueprint.users"))
    db.session.delete(user)  # Assuming db is your SQLAlchemy instance
    db.session.commit()
    flash('تم حذف المستخدم', 'success')
    return redirect(url_for("authentication_blueprint.users"))


@blueprint.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    total_users = Users.query.count()
    active_users = Users.query.filter_by(is_active=True).count()
    users = Users.query.all()
    
    return render_template(
        'accounts/admin.html',
        total_users=total_users,
        active_users=active_users,
        users=users
    )
    
    
@blueprint.route('/admin/generate-cert', methods=['POST'])
@Log.add_log("إنشاء شهادة")
@login_required
def admin_generate_cert():
    try:
        ic("Generating certificate")
        # Call your certificate generation function
        cert_path = generate_certificate()
        # ic(cert_path)
        
        # Send the file for download
        return send_file(
            cert_path,
            as_attachment=True,
            download_name='database_certificate.crt',
            mimetype='application/x-x509-ca-cert'
        )
    except Exception as e:
        flash(f'Error generating certificate: {str(e)}', 'danger')
        return redirect(url_for('authentication_blueprint.admin_dashboard'))
    
# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    """
    A route function that handles unauthorized access attempts.

    This function is a route handler for the '/' endpoint. It is responsible for handling unauthorized access attempts by returning a rendered template for the 'home/page-403.html' page and a status code of 403.

    Returns:
        A tuple containing the rendered template and the status code.
    """
    session['original_url'] = request.url
    # return redirect(url_for('authentication_blueprint.login'))
    return render_template("home/page-403.html"), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    """
    A route function that handles access forbidden errors.

    This function is a route handler for the '/' endpoint. It is responsible for handling access forbidden errors by returning a rendered template for the 'home/page-403.html' page and a status code of 403.

    Parameters:
        error (Exception): The access forbidden error that occurred.

    Returns:
        A tuple containing the rendered template and the status code.
    """
    session['original_url'] = request.url
    # return redirect(url_for("authentication_blueprint.login"))
    return render_template('home/page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    """
    A route function that handles 404 errors.

    This function is a route handler for the '/' endpoint. It is responsible for handling 404 errors by returning a rendered template for the 'home/page-404.html' page and a status code of 404.

    Parameters:
        error (Exception): The 404 error that occurred.

    Returns:
        A tuple containing the rendered template and the status code.
    """
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    """
    A route function that handles internal server errors.

    This function is a route handler for the '/' endpoint. It is responsible for handling internal server errors by returning a rendered template for the 'home/page-500.html' page and a status code of 500.

    Parameters:
        error (Exception): The internal server error that occurred.

    Returns:
        A tuple containing the rendered template and the status code.
    """
    return render_template('home/page-500.html'), 500
