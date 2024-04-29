from ast import literal_eval
import datetime
import json
from flask import render_template, request
from sqlalchemy import func
from apps.profiles.models import Influencer
from apps.reports import blueprint

from apps.reports.models import ScanLog, ScanResults

from icecream import ic

from apps.social.models import SocialAccount



@blueprint.route("/scanresults")
# @login_required
def scanResults():
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    search_terms = request.args.get("q", "")
    from_date = request.args.get("from_date", datetime.date.min)
    to_date = request.args.get("to_date",datetime.date.max)
    from_date=from_date if from_date else datetime.date.min
    to_date=to_date if to_date else datetime.date.max

    # filter influencers
    scanresults = (
        ScanResults.query.filter(
            ScanResults.socialaccount.has(
                (
                    SocialAccount.influencer.has(
                        (Influencer.full_name.ilike(f"%{search_terms}%"))
                        | (SocialAccount.username.ilike(f"%{search_terms}%"))
                    )
                )
            ),
            ScanResults.creation_date >= from_date,
            ScanResults.creation_date <= to_date,
        ).paginate(page=page, per_page=per_page)
        # .all()
    )

    # scanlogs = ScanLog.query.all()  # Fetch all influencers
    return render_template("reports/scanresults.html", scanresults=scanresults, from_date=from_date, to_date=to_date, search_terms=search_terms)

#////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/scanlog")
# @login_required
def scanLog():
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    # search_terms = request.args.get("q", "")
    from_date = request.args.get("from_date", datetime.date.min)
    to_date = request.args.get("to_date", datetime.date.max)
    from_date = from_date if from_date else datetime.date.min
    to_date = to_date if to_date else datetime.date.max

    # filter influencers
    scanlog = (
        ScanLog.query
        .filter(
            ScanLog.creation_date >= from_date,
            ScanLog.creation_date <= to_date,
        )
        .paginate(page=page, per_page=per_page)
    )
    
    for item in scanlog.items:
        ic(item.failures.items)
        # = literal_eval(item.failures)

    return render_template(
        "reports/scanlog.html",
        scanlog=scanlog,
        from_date=from_date,
        to_date=to_date,
        # search_terms=search_terms,
    )
