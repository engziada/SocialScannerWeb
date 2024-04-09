
import datetime
import html
from bs4 import BeautifulSoup
from icecream import ic
import instaloader
import json
import requests


profile_data: dict = {
    "username": '',
    "platform": '',
    "public_profile_name": '',
    "followers": 0,
    "likes": 0,
    "posts": 0,
    "profile_picture": '',
    "bio_text": '',
    "external_url": '',
    "time_taken": 0,
    "Error": ''
}

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
    profile_data["time_taken"] = duration.total_seconds()
    ic(profile_data)
    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def tiktok(username:str)->dict:
    
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
    ic(r.status_code)

    if r.status_code != 200:
        profile_data["Error"] = f"Failed to fetch the URL, HTTP status code: {r.status_code}"
        return profile_data
    
    # Parse the HTML content
    soup = BeautifulSoup(r.text, "html.parser")

    # Find the script element by ID
    script_element = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__")

    # Check if the script element exists
    if script_element is None:
        profile_data["Error"] = "Script element with ID '__UNIVERSAL_DATA_FOR_REHYDRATION__' not found."
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
    ic(r.status_code)

    if r.status_code != 200:
        profile_data["Error"] = (f"Failed to fetch the URL, HTTP status code: {r.status_code}")
        return profile_data

    # Parse HTML content
    soup = BeautifulSoup(r.text, "html.parser")

    profile_section = soup.find("div", class_=lambda x: x and "PublicProfileCard_userDetailsContainer" in x)

    if profile_section is None:
        profile_data["Error"] = "Profile section not found."
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
        "followers": follower_count,
        "likes": 0,
        "posts": 0,
        "profile_picture": profile_image,
        "bio_text": subtitle,
        "external_url": url,
        # "time_taken": duration.total_seconds(),
    }
    return profile_data

#////////////////////////////////////////////////////////////////////////////////////////

def instagram(username:str)-> dict:
    profile_data: dict = None
    L = instaloader.Instaloader()

    # Login (if required)
    # L.load_session_from_file('username')

    t1 = datetime.datetime.now()

    # Retrieve profile details
    profile = instaloader.Profile.from_username(L.context, "_eyad_")

    # Get profile details
    # ic(profile.followees)
    # ic(profile.external_url)
    # ic(profile.is_private)
    # ic(profile.is_verified)
    # ic(profile.posts)
    # ic(profile.igtvcount)
    # ic(profile.saved_media)
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
    
    duration = datetime.datetime.now() - t1

    profile_data: dict = {
        "username": profile.username,
        "platform": "Instagram",
        "public_profile_name": profile.full_name,
        "followers": profile.followers,
        "likes": 0,
        "posts": 0,
        "profile_picture": profile.biography,
        "bio_text": "",
        "external_url": profile.profile_pic_url,
        "time_taken": duration.total_seconds(),
    }
    return profile_data