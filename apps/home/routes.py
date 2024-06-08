import datetime
from flask import  redirect, render_template, request, flash, session, url_for
from apps.home import blueprint
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps.home.models import Log
from apps.home.forms import SearchForm
from apps.home.util import search_user_profile, get_summerized_report
from apps.globals.util import import_content_from_excel

from apps.social.models import Platform, SocialAccount

from werkzeug.datastructures.file_storage import FileStorage

from icecream import ic


@blueprint.route('/index')
@login_required
def index():
    """
    A route function that handles the '/index' endpoint.

    This function is responsible for rendering the 'home/index.html' template and returning it to the client.
    It requires the user to be logged in.

    Parameters:
        None

    Returns:
        The rendered 'home/index.html' template with the 'segment' variable set to 'index' and the 'stats' variable set to the result of the 'get_summerized_report()' function.
    """
    statistics = get_summerized_report()
    return render_template('home/index.html', segment='index', stats=statistics)


@blueprint.route('/<template>')
@login_required
def route_template(template):
    """
    A route function that handles dynamic routing for HTML templates.

    This function is responsible for serving HTML templates based on the provided template name. It takes a template parameter, which is a string representing the name of the template file. The function appends the '.html' extension to the template name if it doesn't already end with '.html'.

    The function first detects the current page by calling the get_segment() function with the request object. The get_segment() function extracts the last segment from the request path and returns it. If the segment is an empty string, it is set to 'index'.

    The function then attempts to render the template by calling the render_template() function with the template name and the segment variable. If the template is found, it is rendered with the segment variable and returned as the response.

    If a TemplateNotFound exception is raised, indicating that the template file does not exist, the function renders the 'home/page-404.html' template and returns it with a 404 status code.

    If any other exception is raised, the function renders the 'home/page-500.html' template and returns it with a 500 status code.

    Parameters:
        template (str): The name of the template file.

    Returns:
        The rendered HTML template if it exists, or the 'home/page-404.html' or 'home/page-500.html' template with the corresponding status code.
    """
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    """
    Get the segment from the request path and return it.

    Parameters:
        request (object): The request object containing the path.

    Returns:
        str: The segment extracted from the request path. If the segment is an empty string, it is set to 'index'.
        None: If an exception occurs while extracting the segment.
    """
    try:
        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


#////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/log", methods=["GET", "POST"])
@login_required
def log():
    """
    Renders the log page with logs based on the specified date range.

    Parameters:
        None

    Returns:
        str: The rendered log page template with logs, from_date, and to_date.
    """
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    from_date = request.args.get("from_date", datetime.date.min)
    to_date = request.args.get("to_date", datetime.date.max)
    from_date=from_date if from_date else datetime.date.min
    to_date=to_date if to_date else datetime.date.max

    logs = (
        Log.query.filter(Log.creation_date >= from_date, Log.creation_date <= to_date)
        .order_by(Log.creation_date.desc())
        .order_by(Log.creation_time.desc())
        .paginate(page=page, per_page=per_page)
    )

    return render_template("home/log.html", logs=logs, from_date=from_date, to_date=to_date)

#////////////////////////////////////////////////////////////////////////////////////////

# profile_data: dict = {
#     "username": '',
#     "platform": '',
#     "public_profile_name": '',
#     "followers": 0,
#     "likes": 0,
#     "posts": 0,
#     "profile_picture": '',
#     "bio_text": '',
#     "external_url": '',
#     "time_taken": 0,
#     "error": ''
#     "existing_record":""
# }


@blueprint.route("/search", methods=["GET", "POST"])
@login_required
@Log.add_log("عملية بحث")
def search():
    """
    Handles the search functionality on the "/search" route.

    This function is decorated with the `@blueprint.route("/search", methods=["GET", "POST"])` decorator, which means it is the handler for the "/search" route with both GET and POST methods.

    Parameters:
        None

    Returns:
        The rendered template for the "home/search.html" page.

    Raises:
        None
    """
    form = SearchForm()
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]

    profile_data = None

    if form.validate_on_submit():
        platform = form.platform.data
        username = form.username.data

        try:
            existingRecord = SocialAccount.query.filter_by(username=username, platform_id=platform).first()
            profile_data = search_user_profile(username, platform)
            if profile_data.get("error") is not None:
                flash(profile_data["error"], "danger")
            elif existingRecord:
                profile_data["existing_record"] = existingRecord
                flash("الحساب موجود بالفعل, تم تحويلك على صفحة تعديل/عرض الحساب", "danger")
                return redirect(
                    url_for(
                        "social_blueprint.socialaccount_edit",
                        socialaccount_id=existingRecord.id,
                    )
                )
            else:
                session["profile_data"] = profile_data
        except Exception as e:
            ic('Error in Search: ',e)
            flash(f"Error: {str(e)}")  # Handle backend errors gracefully

    return render_template("home/search.html", form=form, profile_data=profile_data)


# ////////////////////////////////////////////////////////////////////////////////////////

# ////////////////////////////////////////////////////////////////////////////////////////


# @blueprint.route("/start_scan", methods=["GET", "POST"])
# @login_required
# @Log.add_log("عملية مسح")
# def start_scan():
#     current_app.sched.run_job("job1")
#     flash("تم بدء عملية المسح", "success")
#     return redirect(url_for("home_blueprint.index"))
