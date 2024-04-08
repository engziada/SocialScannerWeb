
import datetime
from select import select
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from icecream import ic
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

import instaloader

from icecream import ic


# Set Firefox options to run in headless mode
firefox_options = FirefoxOptions()
# firefox_options.headless = True
# firefox_options.add_argument("-headless")
# Initialize WebDriver with Firefox and set options

# # Set Chrome options to run in headless mode
# chrome_options = ChromeOptions()
# chrome_options.add_argument("--headless")  # Enable headless mode
# chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (necessary in headless mode)
# chrome_options.add_argument("--window-size=1920x1080")  # Set window size
# # Initialize WebDriver with Chrome and set options
# driver = webdriver.Chrome(options=chrome_options)


def search_user_profile(username:str, platform:str) -> dict:
    """
    Search for a user profile on a specific platform
    :param username: The username to search for
    :param platform: The platform to search on
    :return: A dictionary containing the user's profile data
    """

    ic(username, platform)
    if platform == '1':
        profile_data = snapchat(username)
    elif platform == '2':
        profile_data = instagram(username)
    elif platform == '3':
        profile_data = tiktok(username)
    else:
        ic("Invalid platform value")
        raise ValueError("Invalid platform value")

    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def tiktok(username:str)->dict:
    
    profile_data: dict = None
    url = f"https://www.tiktok.com/@{username}"
    t1 = datetime.datetime.now()
    # Open the TikTok website
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    # Dismiss the popup modal if present# Dismiss the login modal if present
    try:
        login_modal = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "loginContainer")))
        # Press ESC key
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except:
        ic("Login modal not found")

    # Dismiss the captcha dialog if present
    try:
        captcha_dialog = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "captcha_verify_bar")))
        # Locate the close icon and click it
        close_icon = captcha_dialog.find_element(By.CLASS_NAME, "verify-bar-close")
        close_icon.click()
    except:
        ic("Captcha dialog not found")

    # Parse HTML content
    soup = BeautifulSoup(driver.page_source, "html.parser")

    profile_section = soup.find("div", class_=lambda x: x and "DivShareLayoutHeader" in x)

    if profile_section is None:
        ic("Profile section not found.")
        return profile_data
    else:
        ic("profile section found")

        # Extract profile details
        profile_name = profile_section.find("h2", attrs={"data-e2e": "user-subtitle"}).text.strip()
        follower_count = profile_section.find("strong", attrs={"data-e2e": "followers-count"}).text.strip()
        likes_count = profile_section.find("strong", attrs={"data-e2e": "likes-count"}).text.strip()
        user_bio = profile_section.find("h2", attrs={"data-e2e": "user-bio"}).text.strip()
        profile_image = profile_section.find("div", attrs={"data-e2e": "user-avatar"}).find("img")["src"]

    # Close the browser when done
    driver.quit()
    duration = datetime.datetime.now() - t1
    
    profile_data: dict = {
        "username": username,
        "platform": "TikTok",
        "public_profile_name": profile_name,
        "followers": follower_count,
        "likes": likes_count,
        "posts": 0,
        "profile_picture": profile_image,
        "bio_text": user_bio,
        "external_url": url,
        "time_taken": duration.total_seconds(),
    }
    
    return profile_data

# ////////////////////////////////////////////////////////////////////////////////////////

def snapchat(username:str)->dict:
    profile_data: dict = None
    url = f"https://www.snapchat.com/add/{username}"
    t1 = datetime.datetime.now()
    # Open the Snapchat website
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)

    try:
        # Wait for the toast to appear
        toast = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "ToastBodyExpanded_toastBodyExpanded")))
        # Dismiss the toast by pressing the ESC key
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        print("Toast dismissed successfully.")
    except:
        ic("Login modal not found")

    # Parse HTML content
    soup = BeautifulSoup(driver.page_source, "html.parser")

    profile_section = soup.find("div", class_=lambda x: x and "DesktopPublicProfile_profileCardWrapper" in x)
    if profile_section is None:
        ic("Profile section not found.")
        return profile_data
    else:
        ic("profile section found")
        # Extract profile details
        profile_name = profile_section.find("span", class_=lambda x: x and "PublicProfileDetailsCard_displayNameText" in x).text.strip()
        follower_count = profile_section.find("div",class_=lambda x: x and "PublicProfileDetailsCard_desktopSubscriberText" in x,).text.strip()
        subtitle = profile_section.find("div", class_=lambda x: x and "PublicProfileCard_desktopTitle" in x).text.strip()
        profile_image = soup.find("picture", class_=lambda x: x and "ProfilePictureBubble_webPImage" in x).find("img")["srcset"]
        # address = profile_section.find("address").text.strip()

        # ic(address)

    # Close the browser when done
    driver.quit()

    duration = datetime.datetime.now() - t1

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
        "time_taken": duration.total_seconds(),
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