
import datetime
from genericpath import isfile
from os import listdir, makedirs, path
import random
from bs4 import BeautifulSoup
from flask import current_app, url_for
from icecream import ic
import instaloader
import json
import requests
from sqlalchemy import func
from werkzeug.utils import secure_filename

from apps.profiles.models import Influencer
from apps.reports.models import ScanLog
from apps.social.models import Platform, SocialAccount
from apps.authentication.models import Users

from apps import db


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
#     "Error": ''
# }

def search_user_profile(username:str, platform:str) -> dict:
    """
    Search for a user profile on a specific platform
    :param username: The username to search for
    :param platform: The platform to search on
    :return: A dictionary containing the user's profile data
    """
    t1 = datetime.datetime.now()

    if platform == '1':
        profile_data = snapchat(username)
    elif platform == '2':
        profile_data = instagram(username)
    elif platform == '3':
        profile_data = tiktok(username)
    else:
        raise ValueError("Invalid platform value")
    
    duration = datetime.datetime.now() - t1
    profile_data["time_taken"] = f"{duration.total_seconds():.1f} ثانية"
    # ic(profile_data)
    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def tiktok(username:str)->dict:
    profile_data = {}
    url = f"https://www.tiktok.com/@{username}"

    payload = {
        "api_key": "e5b023a283332ce09fcbf4112d9d9cb5",
        "url": url,
        "country_code": "eu",
        "device_type": "desktop",
        "session_number": 123,
    }
    r = requests.get("https://api.scraperapi.com/", params=payload)

    # Print the status code
    # ic(r.status_code)

    if r.status_code != 200:
        profile_data["error"] = "إسم المستخدم غير موجود على هذه المنصة"
        return profile_data
    
    # Parse the HTML content
    soup = BeautifulSoup(r.text, "html.parser")

    # Find the script element by ID
    script_element = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

    # Check if the script element exists
    if script_element is None:
        profile_data["error"] = "خطأ أثناء قراءة البيانات من المنصة"
        return profile_data

    # Extract the text content of the script element
    json_text = script_element.text.strip()
    # Parse the JSON data
    json_data = json.loads(json_text)
    try:
        user_data = json_data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]["user"]
        stats_data = json_data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]["stats"]
    except KeyError:
        profile_data["Error"] = "Could not find the required data in the JSON structure."
        return profile_data

    profile_data: dict = {
        "username": username,
        "platform": "TikTok",
        "public_profile_name": user_data["nickname"],
        "followers": stats_data['followerCount'],
        "likes": stats_data['heartCount'],
        "posts": 0,
        "profile_picture": user_data['avatarLarger'],
        "bio_text": user_data['signature'],
        "external_url": url,
        # "time_taken": duration.total_seconds(),
    }  
    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def snapchat(username:str)->dict:
    profile_data = {}
    url = f"https://www.snapchat.com/add/{username}"

    # Fetch the URL using Scraper API
    payload = {
        "api_key": "e5b023a283332ce09fcbf4112d9d9cb5",
        "url": url,
        "country_code": "eu",
        "device_type": "desktop",
        "session_number": 345,
    }
    r = requests.get("https://api.scraperapi.com/", params=payload)

    # Print the status code
    # ic(r.status_code)

    if r.status_code != 200:
        profile_data["error"] = "إسم المستخدم غير موجود على هذه المنصة"
        return profile_data

    # Parse HTML content
    soup = BeautifulSoup(r.text, "html.parser")

    profile_section = soup.find("div", class_=lambda x: x and "PublicProfileCard_userDetailsContainer" in x)

    if profile_section is None:
        profile_data["error"] = "خطأ أثناء قراءة البيانات من المنصة"
        return profile_data

    # Extract profile details
    profile_name = profile_section.find(
        "span", class_=lambda x: x and "PublicProfileDetailsCard_displayNameText" in x
    ).text.strip()
    follower_count = profile_section.find("div",class_=lambda x: x and "SubscriberText" in x).text.strip()
    subtitle = soup.find("div", class_=lambda x: x and "PublicProfileCard_mobileTitle" in x).text.strip()
    profile_image = soup.find("picture", class_=lambda x: x and "ProfilePictureBubble_webPImage" in x).find("img")["srcset"]
    # address = profile_section.find("address").text.strip()

    profile_data: dict = {
        "username": username,
        "platform": "SnapChat",
        "public_profile_name": profile_name,
        "followers": format_numbers_snapchat(follower_count),
        "likes": 0,
        "posts": 0,
        "profile_picture": profile_image,
        "bio_text": subtitle,
        # "address": address,
        "external_url": url,
        # "time_taken": duration.total_seconds(),
    }
    return profile_data

#////////////////////////////////////////////////////////////////////////////////////////

def instagram(username:str)-> dict:
    profile_data = {}
    L = instaloader.Instaloader()

    # Login (if required)
    # L.login("engziada", "mazisvip")
    # L.two_factor_login(two_factor_code)
    # L.load_session_from_file('engziada')

    # Retrieve profile details
    profile = instaloader.Profile.from_username(L.context, username)
    if not profile:
        profile_data["error"] = "إسم المستخدم غير موجود على هذه المنصة"
        return profile_data

    ic(profile.external_url)
    # # Get profile details
    # ic(profile.followees)
    # ic(profile.external_url)
    # ic(profile.is_private)
    # ic(profile.is_verified)
    # ic(profile.igtvcount)
    # ic(profile.mediacount)
    # ic(profile.total_igtv_count)
    # ic(profile.total_saved_media_count)
    # ic(profile.total_timeline_mediacount)
    # ic(profile.timeline_mediacount)
    # ic(profile.timeline_media)
    # ic(profile.timeline_likes)
    # ic(profile.timeline_comments)
    # ic(profile.timeline_caption)
    # ic(profile.timeline)
    # ic(profile.biography)
    # ic(profile.profile_pic_url)
    # ic(profile.profile_pic_url_hd)
    # ic(profile.full_name)
    # ic(profile.username)
    # ic(profile.userid)
    # ic(profile.followers)
    
    

    profile_data: dict = {
        "username": profile.username,
        "platform": "Instagram",
        "public_profile_name": profile.full_name,
        "followers": profile.followers,
        "likes": 0,
        "posts": 0,
        "profile_picture": download_profile_image_instagram(profile.profile_pic_url),
        "bio_text": profile.biography,
        "external_url": profile.external_url,
        # "time_taken": duration.total_seconds(),
    }
    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def format_numbers_snapchat(follower_count_str):
    # Remove ' Subscribers' from the string
    follower_count_str = follower_count_str.split(' ')[0]
    # Remove commas from the string    
    if follower_count_str.endswith('m'):
        return int(float(follower_count_str[:-1]) * 1_000_000)
    elif follower_count_str.endswith('k'):
        return int(float(follower_count_str[:-1]) * 1_000)
    else:
        return int(follower_count_str)


def download_profile_image_instagram(image_url):
    response = requests.get(image_url)
    upload_folder = path.join(current_app.root_path, "static", "profile_pictures")
    if not path.exists(upload_folder):
        makedirs(upload_folder)
    new_filename = secure_filename(f"temp_insta_profile_image.jpg")
    filepath = path.join(upload_folder, new_filename)
    with open(filepath, "wb") as f:
        f.write(response.content)    
    profile_picture_url=url_for("static", filename="profile_pictures/" + new_filename) 
    return profile_picture_url  # Return the path to the downloaded image

# ////////////////////////////////////////////////////////////////////////////////////////

def get_summerized_report()->dict:
    pictures_folder = path.join(current_app.root_path, "static", "profile_pictures")
    pictures = [f for f in listdir(pictures_folder) if isfile(path.join(pictures_folder, f))]
    report = {
        "total_users": Users.query.count(),
        "total_profiles": Influencer.query.count(),
        "total_accounts": SocialAccount.query.count(),
        "total_scans": ScanLog.query.with_entities(ScanLog.creation_date)
        .distinct()
        .count(),
        "last_scan_date": ScanLog.query.order_by(ScanLog.creation_date.desc())
        .first()
        .creation_date if ScanLog.query.first() else None,
        "last_scan_time": ScanLog.query.order_by(ScanLog.creation_time.desc())
        .first()
        .creation_time if ScanLog.query.first() else None,
        "platforms": (
            db.session.query(Platform.name, func.count(ScanLog.id))
            .select_from(Platform)
            .join(SocialAccount)
            .join(ScanLog)
            .group_by(Platform.name)
            .all()
        ),
        "random_pictures": random.sample(pictures, 10),
    }

    return report