import datetime
import re
from flask import g, redirect, render_template, request, flash, send_file, session, url_for
from apps.home import blueprint
from flask_login import login_required
from jinja2 import TemplateNotFound

from apps.home.models import Log
from apps.home.forms import SearchForm
from apps.home.util import search_user_profile, get_summerized_report

from apps.social.models import Platform, SocialAccount
# from apps.home.util import verify_pass, create_default_admin

from icecream import ic


@blueprint.route('/index')
# @login_required
def index():
    statistics = get_summerized_report()
    ic(statistics)
    return render_template('home/index.html', segment='index', stats=statistics)


@blueprint.route('/<template>')
# @login_required
def route_template(template):
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
    try:
        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None


#////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/log", methods=["GET", "POST"])
# @login_required
def log():
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
# @login_required
@Log.add_log("عملية بحث")
def search():
    form = SearchForm()
    form.platform.choices = [(platform.id, platform.name) for platform in Platform.query.all()]

    profile_data = None

    if form.validate_on_submit():
        platform = form.platform.data
        username = form.username.data

        try:
            profile_data = search_user_profile(username, platform)
            if profile_data.get("error") is not None:
                flash(profile_data["error"], "danger")
            existingRecord = SocialAccount.query.filter_by(username=username, platform_id=platform).first()
            if existingRecord:
                profile_data["existing_record"] = existingRecord
                flash("الحساب موجود بالفعل, تم تحويلك على صفحة تعديل/عرض الحساب", "danger")
                return redirect(
                    url_for(
                        "social_blueprint.socialaccount_edit",
                        socialaccount_id=existingRecord.id,
                    )
                )
                # return render_template(
                #     "social/socialaccount_edit.html",
                #     form=form,
                #     socialaccount=existingRecord,
                #     influencer=existingRecord.influencer,
                #     profile_data=profile_data,
                # )
        except Exception as e:
            flash(f"Error: {str(e)}")  # Handle backend errors gracefully

    return render_template("home/search.html", form=form, profile_data=profile_data)


# ////////////////////////////////////////////////////////////////////////////////////////
