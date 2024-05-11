from concurrent.futures import ThreadPoolExecutor
import datetime

from apps.reports.models import ScanResults, ScanLog
from apps.home.util import search_user_profile

from icecream import ic

from apps.social.models import Platform, SocialAccount

# from threading import Lock

# # Create a lock
# db_lock = Lock()

scan_log = {
    "success_count": {},
    "failure_count": {},
    "failures": {},
}

def process_username(app, db_session, platform_id, username, socialaccount_id):
    
    with app.app_context():            
        platform_name = (
            db_session.query(Platform.name)
            .filter(Platform.id == platform_id)
            .scalar()
        )
        # ic(f"Processing username {username} on platform {platform_name}")
        try:
            profile_data = search_user_profile(username, str(platform_id))

            # check first if the profile_data has errors and raise an exception
            if profile_data.get("error"):
                raise Exception(profile_data["error"])
            # ic(profile_data)
            
            # check if ScanResults has existing record with the same profile data
            existing_scanresult = (
                db_session.query(ScanResults)
                .filter(ScanResults.socialaccount_id == socialaccount_id)
                .filter(ScanResults.bio_text == profile_data["bio_text"])
                .filter(ScanResults.followers == profile_data["followers"])
                .filter(ScanResults.likes == profile_data["likes"])
                .filter(ScanResults.posts == profile_data["posts"])
                .first()
            )
            if not existing_scanresult:
                new_scanresults = ScanResults(
                    socialaccount_id=socialaccount_id,
                    public_profile_name=profile_data["public_profile_name"],
                    bio_text=profile_data["bio_text"],
                    profile_picture=profile_data["profile_picture"],
                    followers=profile_data["followers"],
                    likes=profile_data["likes"],
                    posts=profile_data["posts"],
                    external_url=profile_data["external_url"],
                    time_taken=profile_data["time_taken"],
                )
                # update the socialaccount with the new scanresults
                socialaccount = SocialAccount.query.get(socialaccount_id)
                socialaccount.public_profile_name = profile_data["public_profile_name"]
                socialaccount.bio_text = profile_data["bio_text"]
                socialaccount.followers = profile_data["followers"]
                socialaccount.likes = profile_data["likes"]
                socialaccount.posts = profile_data["posts"]
                # with db_lock:
                db_session.add(new_scanresults)
                db_session.commit()
                
            # ic(f"Scan completed for {username} on platform {platform_id}")
            # save the log, check if the platform is already in the log dictionary, add to success count
            scan_log["success_count"][platform_name] = scan_log.get("success_count", {}).get(platform_name, 0) + 1
                
        except Exception as e:
            # msg = f"{username} : {e}"
            # ic(msg)
            # save the log, check if the platform is already in the log dictionary, add to success count
            scan_log["failure_count"][platform_name] = scan_log.get("failure_count", {}).get(platform_name, 0) + 1
            
            # Initialize scan_log["failures"] as an empty dictionary if it doesn't exist
            if "failures" not in scan_log:
                scan_log["failures"] = {}
                scan_log["failures"][platform_name]={}
                scan_log["failures"][platform_name][username] = str(e)
            else:
                if platform_name in scan_log["failures"]:
                    scan_log["failures"][platform_name][username] = str(e)
                else:
                    scan_log["failures"][platform_name] = {username: str(e)}
                    


def scan_database(app,db_session):
    try:
        start_time = datetime.datetime.now()
        socialaccounts=SocialAccount.query.all()

        with ThreadPoolExecutor() as executor:
            tasks = []
            for socialaccount in socialaccounts:
                tasks.append(
                    executor.submit(
                        process_username,
                        app,
                        db_session,
                        socialaccount.platform_id,
                        socialaccount.username,
                        socialaccount.id,
                    )
                )
            for task in tasks:
                task.result()  # Wait for completion and handle exceptions if any

        # ic(scan_log)
        end_time = datetime.datetime.now()
        time_taken = end_time - start_time
        # ic("Database scan completed in ", time_taken)
        minutes = round(time_taken.total_seconds() // 60)
        seconds = round(time_taken.total_seconds() % 60)
        scan_log["time_taken"] = f"{minutes} دقيقة {seconds} ثانية"
        
        # insert into database
        new_scanlog = ScanLog(
            success_count=scan_log["success_count"],
            failure_count=scan_log["failure_count"],
            failures=scan_log["failures"],
            time_taken=str(scan_log["time_taken"]),
        )
        db_session.add(new_scanlog)
        db_session.commit()
        
        ic("Database scan completed in ", time_taken)
        # ic(scan_log)
    except Exception as e:
        msg=f"Error in scan_database: {e}"
        ic(msg)



