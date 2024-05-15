from flask import render_template, flash, send_file
from flask_login import login_required

from apps.globals import blueprint

from apps.globals.util import download_excel
from apps.home.util import get_summerized_report

from icecream import ic


@blueprint.route("/export_to_excel/<model_name>")
@login_required
def export_to_excel(model_name):
    """
    Export data from a specified model to an Excel file and send it as a download.

    Parameters:
        model_name (str): The name of the model to export data from.

    Returns:
        flask.Response: The response object containing the Excel file as a download.

    Raises:
        None
    """
    file_path: str = download_excel(model_name)#.replace("app/", "")
    # ic(file_path)
    if not file_path:
        flash("No data to export", "danger")
        return render_template("home/index.html", segment="index", stats=get_summerized_report())
    return send_file(
        path_or_file=file_path,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
