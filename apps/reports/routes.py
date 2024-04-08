from flask import render_template, redirect, request, url_for, flash
from apps.reports import blueprint

from apps import db

from apps.reports.models import ScanLog
# from apps.home.util import verify_pass, create_default_admin

from icecream import ic



@blueprint.route("/scanlog")
# @login_required
def scanlog():
    scanlogs = ScanLog.query.all()  # Fetch all influencers
    return render_template("reports/scanlogs.html", scanlogs=scanlogs)

#////////////////////////////////////////////////////////////////////////////////////////