from datetime import datetime
from genericpath import isfile
from operator import ge
from os import listdir, makedirs, path
import random
from bs4 import BeautifulSoup
from flask import current_app, url_for,flash
from icecream import ic
import json
import requests
from werkzeug.utils import secure_filename

from apps.profiles.models import Influencer
from apps.reports.models import ScanLog
from apps.social.models import Platform, SocialAccount, SocialAccount_Content
from apps.authentication.models import Users
from apps.content_types.models import Content

from apps import db

import pandas as pd
from sqlalchemy.exc import IntegrityError

from werkzeug.datastructures.file_storage import FileStorage
from werkzeug.utils import secure_filename


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


def search_user_profile(username:str, platform_id) -> dict:
    """
    Search for a user profile on a specific platform
    :param username: The username to search for
    :param platform: The platform to search on
    :return: A dictionary containing the user's profile data
    """
    t1 = datetime.now()

    platform = Platform.query.get(platform_id)
    if platform:
        platform_name_english = platform.name_english.lower().strip()
        function_name = f"{platform_name_english}(username)"
        profile_data = eval(function_name)
    else:
        raise ValueError("المنصة غبر موجودة في قاعدة البيانات")
    
    duration = datetime.now() - t1
    profile_data["time_taken"] = f"{duration.total_seconds():.1f} ثانية"
    profile_data["platform_id"] = platform_id
    profile_data["username"] = username
    profile_data["platform"] = platform.name
    profile_data["platform_name_english"] = platform.name_english
    
    # ic(profile_data)
    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def tiktok(username: str) -> dict:
    """
    Retrieves the profile data of a user from the TikTok platform.

    Args:
        username (str): The username of the user.

    Returns:
        dict: A dictionary containing the profile data of the user. The dictionary has the following keys:
            - "public_profile_name" (str): The public profile name of the user.
            - "followers" (int): The number of followers the user has.
            - "likes" (int): The number of likes the user has.
            - "posts" (int): The number of posts the user has.
            - "profile_picture" (str): The URL of the user's profile picture.
            - "bio_text" (str): The user's bio text.
            - "external_url" (str): The URL of the user's TikTok profile.

            If there is an error retrieving the profile data, the dictionary will also contain the following key:
            - "error" (str): A description of the error that occurred.

    Raises:
        KeyError: If the required data is not found in the JSON structure.

    Note:
        - The function uses the TikTok API to retrieve the profile data.
        - The function handles cases where the user's profile is not found on the TikTok platform.
        - The function uses the BeautifulSoup library to parse the HTML content of the TikTok profile page.
        - The function uses the requests library to send GET requests to the TikTok API and retrieve the profile data.

    Example:
        >>> tiktok("example_user")
        {
            "public_profile_name": "Example User",
            "followers": 1000,
            "likes": 5000,
            "posts": 0,
            "profile_picture": "https://example.com/profile_picture.jpg",
            "bio_text": "This is an example user.",
            "external_url": "https://www.tiktok.com/@example_user"
        }
    """
    profile_data = {}
    url = f"https://www.tiktok.com/@{username}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # proxies = {
    #     "http": "http://10.10.1.10:3128",
    #     "https": "http://10.10.1.10:1080",
    # }

    # r = requests.get(url, headers=headers, proxies=proxies, timeout=5)
    r = requests.get(url, headers=headers, timeout=30)

    # Print the status code
    # ic(r.status_code)

    # ic(r.status_code)
    if r.status_code != 200:
        profile_data["username"] = username
        profile_data["platform"] = "تيك توك"
        profile_data["error"] = "إسم المستخدم غير موجود على هذه المنصة"
        return profile_data
    
    # Parse the HTML content
    soup = BeautifulSoup(r.text, "html.parser")
    # Save the soup to a file
    # with open("tiktok_soup.html", "w", encoding="utf-8") as file:
    #     file.write(str(soup))

    # Find the script element by ID
    script_element = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")
    # ic("script_element found" if script_element else "script_element not found")

    # Check if the script element exists
    if script_element is None:
        profile_data["username"] = username
        profile_data["platform"] = "تيك توك"
        profile_data["error"] = "خطأ أثناء قراءة البيانات من المنصة"
        return profile_data

    # Extract the text content of the script element
    json_text = script_element.text.strip()
    # Parse the JSON data
    json_data = json.loads(json_text)
    try:
        user_data = json_data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]["user"]
        stats_data = json_data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]["stats"]
        # ic(user_data, stats_data)
    except KeyError:
        # ic(json_data)
        profile_data["username"] = username
        profile_data["platform"] = "تيك توك"
        profile_data["error"] = "Could not find the required data in the JSON structure."
        return profile_data

    profile_data: dict = {
        # "username": username,
        # "platform": "TikTok",
        # "platform_id": platform_id,
        "public_profile_name": user_data["nickname"],
        "followers": stats_data["followerCount"],
        "likes": stats_data["heartCount"],
        "posts": 0,
        "profile_picture": user_data["avatarLarger"],
        "bio_text": user_data["signature"],
        "external_url": url,
        # "time_taken": duration.total_seconds(),
    }  
    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def snapchat(username: str) -> dict:
    """
    Retrieves Snapchat profile data for a given username.

    Args:
        username (str): The Snapchat username to retrieve profile data for.

    Returns:
        dict: A dictionary containing the retrieved profile data including the profile name, followers, likes, posts, profile picture, bio text, external URL.
    """
    profile_data = {}
    url = f"https://www.snapchat.com/add/{username}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    # proxies = {
    #     "http": "http://10.10.1.10:3128",
    #     "https": "http://10.10.1.10:1080",
    # }
    
    # r = requests.get(url, headers=headers, proxies=proxies)
    r = requests.get(url, headers=headers, timeout=30)

    if r.status_code != 200:
        profile_data["username"] = username
        profile_data["platform"] = "سناب شات"
        profile_data["error"] = "إسم المستخدم غير موجود على هذه المنصة"
        return profile_data

    # Parse HTML content
    soup = BeautifulSoup(r.text, "html.parser")

    profile_section = soup.find("div", class_=lambda x: x and "PublicProfileCard_userDetailsContainer" in x)

    if profile_section is None:
        profile_data["username"] = username
        profile_data["platform"] = "سناب شات"
        profile_data["error"] = "خطأ أثناء قراءة البيانات من المنصة"
        return profile_data

    # Extract profile details
    profile_name = profile_section.find("span", class_=lambda x: x and "PublicProfileDetailsCard_displayNameText" in x).text.strip()
    follower_count = profile_section.find("div",class_=lambda x: x and "SubscriberText" in x).text.strip()
    subtitle = soup.find("div", class_=lambda x: x and "PublicProfileCard_mobileTitle" in x).text.strip()
    subtitle_line2 = soup.find("a", class_=lambda x: x and "PublicProfileCard_mobileDetail" in x).text.strip() if soup.find("a", class_=lambda x: x and "PublicProfileCard_mobileDetail" in x) else ""
    profile_image = soup.find("picture", class_=lambda x: x and "ProfilePictureBubble_webPImage" in x).find("img")["srcset"]
    # address = profile_section.find("address").text.strip()

    profile_data: dict = {
        # "username": username,
        # "platform": "SnapChat",
        "public_profile_name": profile_name,
        "followers": format_numbers_snapchat(follower_count),
        "likes": 0,
        "posts": 0,
        "profile_picture": profile_image,
        "bio_text": subtitle+'\n'+subtitle_line2,
        # "address": address,
        "external_url": url,
        # "platform_id": platform_id,
        # "time_taken": duration.total_seconds(),
    }
    return profile_data

#////////////////////////////////////////////////////////////////////////////////////////

def instagram(username: str) -> dict:
    """
    Retrieves Instagram profile data for a given user.

    Args:
        username (str): The username of the Instagram account to retrieve data for.

    Returns:
        dict: A dictionary containing the profile data of the Instagram account. The dictionary has the following keys:
            - "public_profile_name" (str): The full name of the Instagram account.
            - "followers" (int): The number of followers the Instagram account has.
            - "likes" (int): The number of likes the Instagram account has.
            - "posts" (int): The number of posts the Instagram account has.
            - "profile_picture" (str): The URL of the Instagram account's profile picture.
            - "bio_text" (str): The biography text of the Instagram account.
            - "external_url" (str): The external URL of the Instagram account.
            If the Instagram account does not exist or there is an error, the dictionary will contain the following key:
            - "error" (str): An error message indicating that the Instagram account does not exist or there was an error.
    """
    profile_data = {}

    url = "https://instagram-scraper-2022.p.rapidapi.com/ig/info_username/"

    querystring = {"user": username}

    headers = {
        "X-RapidAPI-Key": "da003d7174mshaee6e176c7049a0p1fbc23jsnbb794c1a7b60",
        "X-RapidAPI-Host": "instagram-scraper-2022.p.rapidapi.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    }

    response = requests.get(url, headers=headers, params=querystring, timeout=30)
    json_data = response.json()
    ic(json_data)
    
    if json_data.get("status","") != "ok" or json_data.get("answer","") == "bad":
        profile_data["username"] = username
        profile_data["platform"] = "إنستاجرام"
        profile_data["error"] = "إسم المستخدم غير موجود على هذه المنصة"
        return profile_data

        
    user_data = json_data["user"]
    # ic(user_data)

    # ic(
    #     user_data["username"],
    #     user_data["full_name"],
    #     user_data["biography"],
    #     user_data["follower_count"],
    #     user_data["hd_profile_pic_url_info"]["url"],
    #     user_data["hd_profile_pic_versions"][0]["url"],
    #     user_data["hd_profile_pic_versions"][1]["url"],
    #     user_data["profile_pic_url"],
    #     user_data["external_url"],
    #     user_data["contact_phone_number"],
    #     user_data["city_name"],
    #     user_data["page_name"],
    # )

    # Retrieve profile details
    profile_data: dict = {
        # "username": profile.username,
        # "platform": "Instagram",
        "public_profile_name": user_data["full_name"],
        "followers": user_data["follower_count"],
        "likes": 0,
        "posts": user_data["media_count"],
        "profile_picture": download_profile_image_instagram(user_data["profile_pic_url"]),
        "bio_text": user_data["biography"],
        "external_url": user_data["external_url"],
        # "time_taken": duration.total_seconds(),
        # "platform_id": platform_id,
    }
    return profile_data


# ////////////////////////////////////////////////////////////////////////////////////////

def format_numbers_snapchat(follower_count_str):
    """
    Format the follower count string for Snapchat.

    Parameters:
        follower_count_str (str): The follower count string from Snapchat.

    Returns:
        int: The formatted follower count.

    This function takes a follower count string from Snapchat and removes any unnecessary characters. It then converts the string to an integer based on the suffix ('m' for millions, 'k' for thousands) and returns the formatted follower count.

    Example:
        >>> format_numbers_snapchat("1.2m")
        1200000

        >>> format_numbers_snapchat("100k")
        100000

        >>> format_numbers_snapchat("12345")
        12345
    """
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
    """
    Downloads the profile image from the provided image URL, saves it in the static folder, and returns the URL for the saved image.

    Args:
        image_url (str): The URL of the image to download.

    Returns:
        str: The URL for the saved profile picture.
    """
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
    """
    Generates a summary report of various statistics from the database.
    
    Returns:
        dict: A dictionary containing the following statistics:
            - total_users (int): The total number of users in the database.
            - total_profiles (int): The total number of profiles in the database.
            - total_accounts (int): The total number of accounts in the database.
            - total_scans (int): The total number of scans in the database.
            - last_scan_date (datetime.date or None): The date of the last scan in the database, or None if no scans exist.
            - last_scan_time (datetime.time or None): The time of the last scan in the database, or None if no scans exist.
            - platforms (list of tuples): A list of tuples containing the name of each platform and the count of scans for that platform.
            - random_pictures (list of str): A list of filenames of randomly selected pictures from the "profile_pictures" folder.
    """
    pictures_folder = path.join(current_app.root_path, "static", "profile_pictures")
    pictures = [f for f in listdir(pictures_folder) if isfile(path.join(pictures_folder, f))]
    last_scan = ScanLog.query.order_by(ScanLog.creation_date.desc(), ScanLog.creation_time.desc()).first()
    platforms = Platform.query.all()
    platform_counts = [(platform.name, SocialAccount.query.filter_by(platform_id=platform.id).count()) for platform in platforms]
    
    report = {
        "total_users": Users.query.count(),
        "total_profiles": Influencer.query.count(),
        "total_accounts": SocialAccount.query.count(),
        "accounts_per_platform": platform_counts,
        "total_scans": ScanLog.query.count(),
        "last_scan_date": last_scan.creation_date if last_scan else None,
        "last_scan_time": last_scan.creation_time if last_scan else None,
        "last_scan_duration": last_scan.time_taken if last_scan else None,
        "platforms": platform_counts,
        "random_pictures": random.sample(pictures, 10),
    }

    return report

# ////////////////////////////////////////////////////////////////////////////////////////

def import_content_from_excel(file:FileStorage,selected_option:str) -> bool:
    try:
        file_extension = path.splitext(file.filename)[1]
        file_path=path.join(current_app.root_path, "import" + file_extension)
        with open(file_path, 'wb') as f:
            f.write(file.read())
    except Exception as e:
        flash(f"خطأ أثناء نسخ الملف: {e}", "danger")
        return False

    if selected_option == "contents":
        # Define the column names
        column_names = ["name", "description"]  # Add other column names here as necessary
        # Read the CSV file
        df = pd.read_csv(file_path, names=column_names, header=None, encoding="utf-8")
        # Iterate over the rows of the DataFrame
        for index, row in df.iterrows():
            # Create a new Content object
            content = Content.query.filter_by(name=row["name"].strip()).first()
            if content:
                continue
            content = Content(
                name=row["name"].strip(),
                description=str(row.get("description", "")).strip(),
            )
            # Add the new Content object to the session
            db.session.add(content)
            
    elif selected_option == "accounts":
        # Define the column names
        column_names = ["username", "platform_id", "influencer","content"]
        # Read the CSV file
        df = pd.read_csv(file_path, names=column_names, header=None, encoding="utf-8")
        # Iterate over the rows of the DataFrame
        for index, row in df.iterrows():
            # Create a new SocialAccount object
            # Check if there is a SocialAccount with the same username
            existing_social_account = SocialAccount.query.filter_by(username=row["username"].strip()).first()
            if existing_social_account:
                continue
        
            influencer = Influencer.query.filter_by(full_name=row["influencer"].strip()).first()
            if influencer:
                influencer_id = influencer.id
            else:
                # flash(f"Influencer with full name {row['influencer']} not found", "danger")
                continue

            social_account = SocialAccount(
                username=row["username"].strip(),
                platform_id=row.get("platform_id"),
                influencer_id=influencer_id,
            )
            # Add the new SocialAccount object to the session
            db.session.add(social_account)
            
            content = Content.query.filter_by(name=row["content"].strip()).first()
            if content:
                content_id = content.id
            else:
                # Handle the case when the content does not exist
                continue

            # Create a new record in the socialaccount_contents table
            socialaccount_content = SocialAccount_Content(
                socialaccount_id=social_account.id,
                content_id=content_id
            )
            # Add the new record to the session
            db.session.add(socialaccount_content)
            
    elif selected_option == "profiles":
        # Define the column names
        column_names = ["full_name", "gender", "country", "city", "phone", "email", "profile_picture"]
        # Read the CSV file
        df = pd.read_csv(file_path, names=column_names, header=None, encoding="utf-8")
        # Iterate over the rows of the DataFrame
        for index, row in df.iterrows():
            # Create a new Influencer object
            # Check if there is an influencer with the same full_name
            existing_influencer = Influencer.query.filter_by(full_name=row["full_name"].strip()).first()
            if existing_influencer:
                continue
            
            influencer = Influencer(
                full_name=str(row["full_name"]).strip(),
                gender=str(row.get("gender", "")).strip(),
                country=str(row.get("country", "")).strip(),
                city=str(row.get("city", "")).strip(),
                phone=str(row.get("phone", "")).strip(),
                email=str(row.get("email", "")).strip(),
                profile_picture=str(row.get("profile_picture", "")).strip(),
            )
            # Add the new Influencer object to the session
            db.session.add(influencer)
            
    else:
        flash("الخيار المحدد غير مدعوم", "danger")
        return False

    # Commit the session to save the new Content objects to the database
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        flash(f"خطأ أثناء إستيراد البيانات: {e}", "danger")
        ic(e)
        return False