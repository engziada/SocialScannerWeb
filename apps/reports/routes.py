import datetime
import math

from flask import Response, flash, redirect, render_template, request, url_for
from flask_login import login_required

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import aliased

from apps.content_types.models import Content
from apps.reports import blueprint
from apps import db

from apps.profiles.models import Influencer
from apps.reports.models import ScanLog, ScanResults
from apps.social.models import Platform, SocialAccount, SocialAccount_Content

from icecream import ic
from dateutil.relativedelta import relativedelta

from dateutil import parser
import tablib

@blueprint.route("/scanresults")
@login_required
def scanResults():
    """
    Retrieves scan results based on the specified search criteria and paginates the results.

    Returns:
        A rendered HTML template of the scan results page, including the paginated scan results,
        the specified search terms, the specified date range, and the current page number.

    Parameters:
        None

    Raises:
        None
    """
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    search_terms = request.args.get("q", "")
    from_date = request.args.get("from_date", "01/01/2024")
    to_date = request.args.get("to_date", datetime.datetime.today().strftime("%m/%d/%Y"))
    from_date = from_date if from_date else "01/01/2024"
    to_date = to_date if to_date else datetime.datetime.today().strftime("%m/%d/%Y")

    # filter influencers
    scanresults = ScanResults.query.filter(
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
    ).paginate(page=page, per_page=per_page, error_out=False)

    # scanlogs = ScanLog.query.all()  # Fetch all influencers
    return render_template("reports/scanresults.html", scanresults=scanresults, from_date=from_date, to_date=to_date, search_terms=search_terms)

#////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/scanlog")
@login_required
def scanLog():
    """
    Retrieves scan logs based on the specified date range and paginates the results.

    Returns:
        A rendered HTML template of the scan log page, including the paginated scan logs,
        the specified date range, and the current page number.

    Parameters:
        None

    Raises:
        None
    """
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    # search_terms = request.args.get("q", "")
    from_date = request.args.get("from_date", "01/01/2024")
    to_date = request.args.get("to_date", datetime.datetime.today().strftime("%m/%d/%Y"))
    from_date = from_date if from_date else "01/01/2024"
    to_date = to_date if to_date else datetime.datetime.today().strftime("%m/%d/%Y")

    # filter influencers
    scanlog = (
        ScanLog.query.filter(
            ScanLog.creation_date >= from_date,
            ScanLog.creation_date <= to_date,
        )
        .order_by(
            ScanLog.creation_date.desc()
        )  # Add this line to order by creation_date descending
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    return render_template(
        "reports/scanlog.html",
        scanlog=scanlog,
        from_date=from_date,
        to_date=to_date,
        # search_terms=search_terms,
    )

# ////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/socialaccounts")
@login_required
def socialaccounts():
    """
    Route decorator for the "/socialaccounts" endpoint.
    Requires the user to be logged in.
    
    Parameters:
    None
    
    Returns:
    A rendered HTML template of the social accounts page, including the paginated social accounts,
    the specified date range, and the search terms.
    """
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    search_terms = request.args.get("q", "")
    from_date = request.args.get("from_date", '01/01/2024')
    to_date = request.args.get("to_date", datetime.datetime.today().strftime("%m/%d/%Y"))
    from_date = from_date if from_date else "01/01/2024"
    to_date = to_date if to_date else datetime.datetime.today().strftime("%m/%d/%Y")
    content= request.args.get("content", "")
    platform= request.args.get("platform", "")
    gender= request .args.get("gender", "")
    
    contents = Content.query.all()
    platforms=Platform.query.all()
    
    query = SocialAccount.query
    if search_terms:
        search_condition = or_(
            Influencer.full_name.ilike(f"%{search_terms}%"),
            SocialAccount.username.ilike(f"%{search_terms}%")
        )
        query = query.filter(SocialAccount.influencer.has(search_condition))
    if gender:
        query = query.filter(SocialAccount.influencer.has(Influencer.gender.ilike(f"%{gender}%")))
    if content:
        if content == 'محتوى غير مخصص':
            query = query.filter(~SocialAccount.contents.any())
        else:
            query = query.filter(SocialAccount.contents.any(Content.name.ilike(f"%{content}%")))    
    if platform:
        query = query.filter(SocialAccount.platform.has(Platform.name.ilike(f"%{platform}%")))
    if from_date and to_date:
        date_condition = and_(
            SocialAccount.creation_date >= from_date,
            SocialAccount.creation_date <= to_date
        )
        query = query.filter(date_condition)
    socialaccounts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        "reports/socialaccounts.html",
        socialaccounts=socialaccounts,
        from_date=from_date,
        to_date=to_date,
        search_terms=search_terms,
        contents=contents,
        platforms=platforms,
        selected_content=content,
        selected_platform=platform,
        selected_gender=gender,
    )


@blueprint.route("/export_socialaccounts")
def export_socialaccounts():
    try:
        # ic(request.args)
        # Get the filter parameters from the query string
        search_terms = request.args.get('q', '')
        from_date = request.args.get("from_date", '01/01/2024')
        to_date = request.args.get("to_date", datetime.datetime.today().strftime("%m/%d/%Y"))
        from_date = from_date if from_date else "01/01/2024"
        to_date = to_date if to_date else datetime.datetime.today().strftime("%m/%d/%Y")
        content = request.args.get('content', '')
        platform = request.args.get('platform', '')
        gender = request.args.get('gender', '')

            # Apply the filters to the query
        query = SocialAccount.query
        if search_terms:
            search_condition = or_(
                Influencer.full_name.ilike(f"%{search_terms}%"),
                SocialAccount.username.ilike(f"%{search_terms}%")
            )
            query = query.filter(SocialAccount.influencer.has(search_condition))
        if gender:
            query = query.filter(SocialAccount.influencer.has(Influencer.gender.ilike(f"%{gender}%")))
        if content:
            query = query.filter(SocialAccount.contents.any(Content.name.ilike(f"%{content}%")))
        if platform:
            query = query.filter(SocialAccount.platform.has(Platform.name.ilike(f"%{platform}%")))
        if from_date and to_date:
            date_condition = and_(
                SocialAccount.creation_date >= from_date,
                SocialAccount.creation_date <= to_date
            )
            query = query.filter(date_condition)

        socialaccounts = query.all()
        # ic(query.limit(2).all())
        
        headers = [
            "إسم الملف",
            "إسم الحساب",
            "المنصة",
            "الجنس",
            "المحتوى",
            "المتابعين",
            "الإعجابات",
            "البريد الإلكتروني",
            "رقم الهاتف",
        ]
        data = [
            [
                socialaccount.influencer.full_name,
                socialaccount.username,
                socialaccount.platform.name,
                socialaccount.influencer.gender,
                ", ".join(map(lambda content: content.name, socialaccount.contents)),
                socialaccount.followers,
                socialaccount.likes,
                socialaccount.influencer.email,
                socialaccount.influencer.phone,
            ]
            for socialaccount in socialaccounts
        ]

        # Clean Data (Optional)
        data = [[str(item) if item is not None else "" for item in row] for row in data]

        dataset = tablib.Dataset(*data)  # You don't need to pass headers again here
        dataset.headers = headers
        response = Response(dataset.export('xlsx'), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.headers["Content-Disposition"] = "attachment;filename=social_accounts.xlsx"
        return response

    except Exception as e:
        ic("An error occurred while exporting the social accounts: ", str(e))
        flash(f"An error occurred while exporting the social accounts: {str(e)}", "danger")
        return redirect(url_for("reports_blueprint.socialaccounts"))


# ////////////////////////////////////////////////////////////////////////////////////////

@blueprint.route("/scanresults_report")
@login_required
def scanResults_report():
    """
    Renders the scan results report page.

    This function is a route handler for the "/scanresults_report" endpoint. It is responsible for rendering the scan results report page, which displays a table of social media account information including the username, platform, and followers count for each account. The function retrieves the necessary data from the database based on the specified search terms, date range, and pagination parameters.

    Parameters:
        None

    Returns:
        A rendered HTML template of the scan results report page, including the paginated results table, the specified search terms, the specified date range, and the current page number.

    Raises:
        None
    """
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    search_terms = request.args.get("q", "")
    from_date = request.args.get("from_date", default=str(datetime.datetime.today()))
    interval=request.args.get("intervalRadios", "weekly")
    if from_date:
        # Generate a list of dates based on the interval
        if interval == "weekly":
            dates = [parser.parse(from_date) + datetime.timedelta(days=i * 7) for i in range(6)]
        elif interval == "monthly":
            dates = [parser.parse(from_date) + relativedelta(months=i) for i in range(6)]
        elif interval == "yearly":
            dates = [parser.parse(from_date) + relativedelta(years=i) for i in range(6)]
    else:
        dates = [datetime.datetime.today()]  # Handle invalid interval

    # Convert the dates to strings in the format "YYYY-MM-DD"
    dates = [datetime.datetime.date(date) for date in dates]

    # dates = ["2024-04-27", "2024-04-28", "2024-04-29", "2024-04-30", "2024-04-26"]
    # Create a dictionary to store counts of followers for each username and date
    results_dict = {}
    # Query to get counts of followers for each username and date
    for date in dates:
        subquery = (
            db.session.query(
                SocialAccount.username,
                Platform.name,
                ScanResults.followers,
            )
            .join(ScanResults)
            .join(Platform)
            .filter(func.date(ScanResults.creation_date) == date, SocialAccount.username.ilike(f"%{search_terms}%"))
            .all()
        )

        for username, platform_name, followers_count in subquery:
            if username not in results_dict:
                results_dict[username] = {"platform": platform_name}
            results_dict[username][date] = followers_count

    # Prepare the results to be passed to the template
    results_table = []
    for username, data in results_dict.items():
        row = [username, data["platform"]]
        for date in dates:
            row.append(data.get(date, 0))  # If no data exists for a date, default to 0
        results_table.append(row)

    # Paginate the results
    total_results = len(results_table)
    total_pages = math.ceil(total_results / per_page)
    results_paginated = results_table[(page - 1) * per_page : page * per_page]

    return render_template(
        "reports/scanresults_report.html",
        results_table=results_paginated,
        dates=dates,
        total_pages=total_pages,
        page=page,
        from_date=from_date,
        search_terms=search_terms,
    )


# ////////////////////////////////////////////////////////////////////////////////////////

@blueprint.route("/contents_report")
@login_required
def contents_report():
    # Fetch distinct content types
    content_types = db.session.query(Content.name).distinct().all()

    data = []

    # Count total social accounts
    total_socialaccounts = SocialAccount.query.count()
    # ic(total_socialaccounts)

    for content_type in content_types:
        content_name = content_type[0]  # Extract the name from the tuple

        # Count the total number of social accounts for this content_type
        total_query = (
            db.session.query(func.count(SocialAccount.id))
            .join(SocialAccount_Content, SocialAccount_Content.socialaccount_id == SocialAccount.id)
            .join(Content, SocialAccount_Content.content_id == Content.id)
            .join(Influencer, SocialAccount.influencer_id == Influencer.id)
            .filter(Content.name == content_name)
        )        
        total = total_query.scalar()

        # Count the number of social accounts for each gender
        gender_query = (
            db.session.query(
                Influencer.gender.label("influencers_gender"),
                func.count(SocialAccount.id).label("count_1"),
            )
            .join(
                SocialAccount_Content,
                SocialAccount.id == SocialAccount_Content.socialaccount_id,
            )
            .join(Content, SocialAccount_Content.content_id == Content.id)
            .join(Influencer, SocialAccount.influencer_id == Influencer.id)
            .filter(Content.name == content_name)
            .group_by(Influencer.gender)
        )
        gender_counts = dict(gender_query.all())        
        male = gender_counts.get("ذكر", 0)
        female = gender_counts.get("أنثى", 0)
        other = gender_counts.get("أخرى", 0)
        # Calculate the percentages
        total_percentage = (total / total_socialaccounts) * 100 if total_socialaccounts > 0 else 0
        male_percentage = (male / total) * 100 if total > 0 else 0
        female_percentage = (female / total) * 100 if total > 0 else 0
        other_percentage = (other / total) * 100 if total > 0 else 0

        data.append(
            {
            "content_type": content_name,
            "total": total,
            "total_percentage": f'{total_percentage:.1f}',
            "male_percentage": f'{male_percentage:.1f}',
            "female_percentage": f'{female_percentage:.1f}',
            "other_percentage": f'{other_percentage:.1f}',
            "male":{male},
            "female":{female},
            "other":{other},
            }
        )
    
    # Alias for SocialAccount_Content table
    SAC = aliased(SocialAccount_Content)
    # Query to count uncategorized social accounts and their genders
    uncategorized_accounts_query = (
        db.session.query(Influencer.gender, func.count(SocialAccount.id))
        .outerjoin(SAC, SAC.socialaccount_id == SocialAccount.id)
        .join(Influencer, SocialAccount.influencer_id == Influencer.id)
        .filter(SAC.socialaccount_id == None)  # No related records in the intermediary table
        .group_by(Influencer.gender)
    )
    uncategorized_accounts = uncategorized_accounts_query.all()
    uncategorized_total = sum(count for _, count in uncategorized_accounts)
    gender_counts = dict(uncategorized_accounts_query.all())        

    uncategorized_percentage=0
    if uncategorized_total > 0:
        # Calculate the percentages
        uncategorized_percentage = (
            (uncategorized_total / total_socialaccounts) * 100
            if total_socialaccounts > 0
            else 0
        )
    male = gender_counts.get("ذكر", 0)
    female = gender_counts.get("أنثى", 0)
    other = gender_counts.get("أخرى", 0)
    male_percentage = (male / uncategorized_total) * 100 if uncategorized_total > 0 else 0
    female_percentage = (female / uncategorized_total) * 100 if uncategorized_total > 0 else 0
    other_percentage = (other / uncategorized_total) * 100 if uncategorized_total > 0 else 0

    data.append(
        {
            "content_type": "محتوى غير مخصص",
            "total": uncategorized_total,
            "total_percentage": f"{uncategorized_percentage:.1f}",
            "male_percentage": f"{male_percentage:.1f}",
            "female_percentage": f"{female_percentage:.1f}",
            "other_percentage": f"{other_percentage:.1f}",
            "male": {male},
            "female": {female},
            "other": {other},
        }
    )
    # ic(data)
    return render_template("reports/contents_report.html", data=data)

# ////////////////////////////////////////////////////////////////////////////////////////


@blueprint.route("/daily_report")
@login_required
def daily_report():
    """
    Renders the daily report page with influencer data based on the specified platform.

    Parameters:
        None

    Returns:
        HTML template rendering the daily report with influencer data including influencers, platform, and platforms.
    """
    page = request.args.get("page", 1, type=int)
    per_page = 50  # Number of logs per page

    # content = request.args.get("content", "")
    platform = request.args.get("platform", "")

    # contents = Content.query.all()
    platforms = Platform.query.all()
    
    # filter influencers
    # influencers = Influencer.query.paginate(page=page, per_page=per_page)
    influencers = (Influencer.query.filter(Influencer.socialaccounts.any(SocialAccount.platform.has(Platform.name.ilike(f"%{platform}%"))))).paginate(page=page, per_page=per_page)
    

    return render_template(
        "reports/daily_report.html",
        influencers=influencers,
        platform=platform,
        platforms=platforms,
    )


# ////////////////////////////////////////////////////////////////////////////////////////
