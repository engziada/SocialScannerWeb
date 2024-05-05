from flask import render_template, flash, send_file
from apps.globals import blueprint

from apps.globals.util import download_excel
from apps.home.util import get_summerized_report

from icecream import ic


@blueprint.route("/export_to_excel/<model_name>")
# @login_required
def export_to_excel(model_name):
    file_path: str = download_excel(model_name)#.replace("app/", "")
    if not file_path:
        flash("No data to export", "danger")
        return render_template("home/index.html", segment="index", stats=get_summerized_report())
    return send_file(
        path_or_file=file_path,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
