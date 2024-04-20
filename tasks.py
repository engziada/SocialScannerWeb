# Function for your database scan and logic
from concurrent.futures import ThreadPoolExecutor

from apps.reports.models import ScanLog
from apps.home.util import search_user_profile
from apps.profiles.models import Influencer

from icecream import ic

def process_username(app, db_session, platform_id, username, socialaccount_id):
# The commented out code `# msg=f"Processing {username} on platform {platform_id}"` is creating a
# message string that includes the `username` and `platform_id` variables. The next line `# ic(msg)`
# is using the `icecream` library to log this message using the `ic` function, which provides a
# convenient way to print out debug information with additional context. However, since these lines
# are commented out, they are not currently active in the code execution.
    # msg=f"Processing {username} on platform {platform_id}"
    # ic(msg)
    try:
        with app.app_context():
            profile_data = search_user_profile(username, str(platform_id))
            new_scanlog = ScanLog(
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
            db_session.add(new_scanlog)
            db_session.commit()
            # ic(f"Scan completed for {username} on platform {platform_id}")
    except Exception as e:
        msg = f"Error processing username {username} on platform {platform_id}: {e}"
        ic(msg)


def scan_database(app,db_session):
    try:
        profiles = Influencer.query.all()
        socialaccounts = []
        for profile in profiles:
            for socialaccount in profile.socialaccounts:
                socialaccounts.append({
                    'id': socialaccount.id,
                    'platform_id': socialaccount.platform_id,
                    'username': socialaccount.username
                })

        with ThreadPoolExecutor() as executor:
            futures = []
            for socialaccount in socialaccounts:
                futures.append(
                    executor.submit(
                        process_username,
                        app,
                        db_session,
                        socialaccount["platform_id"],
                        socialaccount["username"],
                        socialaccount["id"],
                    )
                )

            for future in futures:
                future.result()  # Wait for completion and handle exceptions if any

        # Perform scan and logic
        ic("Database scan completed!")
    except Exception as e:
        msg=f"Error in scan_database: {e}"
        ic(msg)



