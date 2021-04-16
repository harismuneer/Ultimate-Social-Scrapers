#!/usr/bin/env python
# coding: utf-8

# # Table of Contents
# 
# Table contents
# -----------------  
# 
# 1. Imports
# 2. Variables
# 3. Identification of images
# 4. Handling of images
# 5. Page Scrolls
# 6. Scraping
# - Downloading friends
# - Down Photos
# - Handling Photo Links
# - Write results to file
# 7. Defining the scraping process
# 8. create the original link
# 9. REad and Run
# 10. Login
# 11. CLI Errors
# 12. CLI Help
# 13. More Global Variables
# 14. RUN!
# 
# ---

# ## Imports

# In[113]:


import argparse
import json
import os
import platform
import sys

# Custom Imports for time banning.
import time
import urllib.request
from random import randint

import utils
import yaml
from ratelimit import limits
from selenium import webdriver
# from selenium_stealth import stealth
from selenium.webdriver import Firefox
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

# -------------------------------------------------------------
# -------------------------------------------------------------


# ## Global Variables

# In[114]:


# Global Variables
driver = webdriver.Firefox()
opts = Options()
opts.add_argument(
    '--user-agent=Mozilla/5.0 CK={} (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'  # noqa: E501
    )
opts.add_argument("headless")
opts.add_argument("no-sandbox")
opts.add_argument("lang=en-US")
opts.add_argument("dns-prefetch-disable")
opts.add_argument("start-maximized")
# opts.add_experimental_option("excludeSwitches", ["enable-automation"])
# opts.add_experimental_option('useAutomationExtension', False)

# stealth(driver,
#         user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36',  # noqa: E501
#         languages=["en-US", "en"],
#         vendor="Google Inc.",
#         platform="Win32",
#         webgl_vendor="Intel Inc.",
#         renderer="Intel Iris OpenGL Engine",
#         fix_hairline=True,
#         )

# Makes sure slower connections work as well
driver.implicitly_wait(25)

# whether to download photos or not
download_uploaded_photos = True
download_friends_photos = False

# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick,
# else if its false then it will open each photo to download it
# and it will take much more time
friends_small_size = False
photos_small_size = False

total_scrolls = 2500
current_scrolls = 0
scroll_time = 9

old_height = 0
facebook_https_prefix = "https://"
facebook_link_body = "mbasic.facebook.com"

# Reducing these values now that a scroll time period has been added
# to avoid rate limit. Actually did not change them.

# Values for rate limiting | lower is slower!
# Last worked at: low=10,high=25,time=600
# Failed at: low=3,high=10,time=300
rtqlow = 10
rtqhigh = 25
# You don't really need to change these at all.
rltime = 600
rhtime = 900

# Traversal speed is solely controlled by this variable
# Vales for time sleep in secs
# Last worked at: min=25,max=40
# Failed at: min=20, max=40
tsmin = 15
tsmax = 30


# CHROMEDRIVER_BINARIES_FOLDER = "bin"
Firefox(executable_path="/usr/local/bin/geckodriver")


# ## Identify images

# In[115]:


###############################################
#     ___    _            _   _  __           #
#    |_ _|__| | ___ _ __ | |_(_)/ _|_   _     #
#     | |/ _` |/ _ \ '_ \| __| | |_| | | |    #
#     | | (_| |  __/ | | | |_| |  _| |_| |    #
#    |___\__,_|\___|_| |_|\__|_|_|  \__, |    #
#                                   |___/     #
#     ___                                     #
#    |_ _|_ __ ___   __ _  __ _  ___  ___     #
#     | || '_ ` _ \ / _` |/ _` |/ _ \/ __|    #
#     | || | | | | | (_| | (_| |  __/\__ \    #
#    |___|_| |_| |_|\__,_|\__, |\___||___/    #
#                         |___/               #
###############################################

# -------------------------------------------------------------
# Identify Image Links
# Important Note! The script scans the profiles and appends thestatus
# links to a list, then downloads them later.
# -------------------------------------------------------------
'''
img_links = [
    x.find_element_by_css_selector("img").get_attribute("src")
    for x in elements
]
'''
# ****************************************************************************
# *                            Get Facebook Images                           *
# ****************************************************************************


# TODO: Replace elements and get working again.
@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def get_facebook_images_url(img_links):
    urls = []

    for link in img_links:
        if link != "None":
            valid_url_found = False
            time.sleep(randint(tsmin, tsmax))
            driver.get(link)

            try:
                while not valid_url_found:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, selectors.get("spotlight"))
                        )
                    )
                    element = driver.find_element_by_xpath(
                        selectors.get("spotlight")
                    )
                    img_url = element.get_attribute("src")

                    if img_url.find(".gif") == -1:
                        valid_url_found = True
                        urls.append(img_url)
            except Exception:
                urls.append("None")
        else:
            urls.append("None")

    return urls


# #### Identifying images notes:
#
# Script needs to do the following in order:
# 1. Locate the image link on the profile page or open it automatically
# 2. Walk through and return all images found
# 3. Locate and click on the "Next" button to get to the next page
# 4. repeat 2-3 until "next" button disappears.
# 5. Return the results.


# -------------------------------------------------------------

##########################################################################################  # noqa: E501
#      ____      _                      __ _ _        ____  _           _                #  # noqa: E501
#     / ___| ___| |_   _ __  _ __ ___  / _(_) | ___  |  _ \| |__   ___ | |_ ___  ___     #  # noqa: E501
#    | |  _ / _ \ __| | '_ \| '__/ _ \| |_| | |/ _ \ | |_) | '_ \ / _ \| __/ _ \/ __|    #  # noqa: E501
#    | |_| |  __/ |_  | |_) | | | (_) |  _| | |  __/ |  __/| | | | (_) | || (_) \__ \    #  # noqa: E501
#     \____|\___|\__| | .__/|_|  \___/|_| |_|_|\___| |_|   |_| |_|\___/ \__\___/|___/    #  # noqa: E501
#                     |_|                                                                #  # noqa: E501
##########################################################################################  # noqa: E501

# --------------------------------------------------------------


def get_profile_photos(img_links, ids):
    lip = []
    time.sleep(randint(tsmin, tsmax))
    # block_check()
    for user_id in ids:
        driver.get(user_id)
        url = driver.current_url
        user_id = create_original_link(url)
        print(url)
        print("\nScraping photos for:", user_id)
        try:
            driver.find_element_by_xpath(
                "//a[contains(text(),'Photos')]").click()
            if presence_of_element_located(By.XPATH, "//a[contains(text(),'See All')]") is True:  # noqa: E501
                driver.find_element_by_xpath(
                    "//a[contains(text(),'See All')]").click()
                WebDriverWait(driver, 20)
                try:
                    gallery_link = [presence_of_element_located(By.XPATH, "//span[text()='See More Photos']")]  # noqa: E501
                    if gallery_link != "None":
                        galleryEnd = False
                        while not galleryEnd:
                            fbimgs = driver.find_element_by_class_name("//a[@class='z ba bb']")  # noqa: E501
                            fbImageLinks = [x.get_attribute("//a[@class='z ba bb']") for x in fbimgs]  # noqa: E501
                            driver.get(fbImageLinks)
                            WebDriverWait(driver, 20)
                            lip = driver.find_element_by_xpath(selectors.get("fullSizeImage")).get_attribute("href")  # noqa: E501
                            lip.append(img_links)
                            if presence_of_element_located(By.XPATH, "//span[text()='See More Photos']") is True:  # noqa: E501
                                driver.find_element_by_xpath(
                                    "//span[text()='See More Photos']").click()
                            else:
                                galleryEnd = True
                    lip = driver.find_element_by_xpath(selectors.get("fullSizeImage")).get_attribute("href")  # noqa: E501
                    lip.append(img_links)
                except Exception as e:
                    raise e
            else:
                fimgs = driver.find_element_by_xpath("//a[@class='ci cj ck']")  # noqa: E501
                fbImageLinks = [x.get_attribute("href") for x in fimgs]
                driver.get(fbImageLinks)
                WebDriverWait(driver, 20)
                lip = driver.find_element_by_xpath(selectors.get("fullSizeImage")).get_attribute("href")  # noqa: E501
                lip.append(img_links)

        except Exception as e:
            raise e
    return img_links

# ## Image Downloader

# In[116]:


# -------------------------------------------------------------

###################################################################
#     ___                                                         #
#    |_ _|_ __ ___   __ _  __ _  ___                              #
#     | || '_ ` _ \ / _` |/ _` |/ _ \                             #
#     | || | | | | | (_| | (_| |  __/                             #
#    |___|_| |_| |_|\__,_|\__, |\___|                             #
#                         |___/                                   #
#     ____                      _                 _               #
#    |  _ \  _____      ___ __ | | ___   __ _  __| | ___ _ __     #
#    | | | |/ _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|    #
#    | |_| | (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |       #
#    |____/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|       #
#                                                                 #
###################################################################

# -------------------------------------------------------------

# takes a url and downloads image from that url
@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def image_downloader(img_links, folder_name):
    img_names = []

    try:
        parent = os.getcwd()
        try:
            folder = os.path.join(os.getcwd(), folder_name)
            utils.create_folder(folder)
            os.chdir(folder)
        except Exception:
            print("Error in changing directory.")
        for link in img_links:
            img_name = "None"

            if link != "None":
                img_name = (link.split(".jpg")[0]).split("/")[-1] + ".jpg"

                # this is the image id when there's no profile pic
                if img_name == selectors.get("default_image"):
                    img_name = "None"
                else:
                    try:
                        # Requesting images too fast will get you blocked too.
                        time.sleep(randint(tsmin, tsmax))
                        urllib.request.urlretrieve(link, img_name)
                    except Exception:
                        img_name = "None"

            img_names.append(img_name)

        os.chdir(parent)
    except Exception:
        print("Exception (image_downloader):", sys.exc_info()[0])

    return img_names

# -------------------------------------------------------------

# -------------------------------------------------------------


# ## Page Scrolls

# In[117]:


# -------------------------------------------------------------

################################################################
#     ____                    ____                 _ _         #
#    |  _ \ __ _  __ _  ___  / ___|  ___ _ __ ___ | | |___     #
#    | |_) / _` |/ _` |/ _ \ \___ \ / __| '__/ _ \| | / __|    #
#    |  __/ (_| | (_| |  __/  ___) | (__| | | (_) | | \__ \    #
#    |_|   \__,_|\__, |\___| |____/ \___|_|  \___/|_|_|___/    #
#                |___/                                         #
################################################################

# -------------------------------------------------------------

# get page height.

def check_height():
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height

# -------------------------------------------------------------

# helper function: used to scroll the page


def scroll():
    global old_height
    current_scrolls = 0

    while True:
        try:
            if current_scrolls == total_scrolls:
                return

            old_height = driver.execute_script(
                "return document.body.scrollHeight")
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.05).until(
                lambda driver: check_height()
            )
            current_scrolls += 1
        except TimeoutException:
            break

    return


# ## Scraping

# In[118]:


# -------------------------------------------------------------

####################################################
#     ____                       _                 #
#    / ___|  ___ _ __ __ _ _ __ (_)_ __   __ _     #
#    \___ \ / __| '__/ _` | '_ \| | '_ \ / _` |    #
#     ___) | (__| | | (_| | |_) | | | | | (_| |    #
#    |____/ \___|_|  \__,_| .__/|_|_| |_|\__, |    #
#                         |_|            |___/     #
####################################################

# -------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def save_to_file(name, elements, status, current_section):
    """helper function used to save links to files"""

    # status 0 = dealing with friends list
    # status 1 = dealing with photos
    # status 2 = dealing with videos
    # status 3 = dealing with about section
    # status 4 = dealing with posts

# ****************************************************************************
# *                             Download Friends                             *
# ****************************************************************************

    try:
        f = None  # file pointer

        if status != 4:
            f = open(name, "w", encoding="utf-8", newline="\r\n")

        results = []
        img_names = []

        # dealing with Friends
        if status == 0:
            # get profile links of friends
            results = [x.get_attribute("href") for x in elements]
            results = [create_original_link(x) for x in results]

            # get names of friends
            people_names = [
                x.find_element(By.CLASS_NAME, "cg").get_attribute("text")
                for x in elements
            ]

# ****************************************************************************
# *                                Down Photos                               *
# ****************************************************************************
            friends_small_size = False
            try:
                if download_friends_photos:
                    if friends_small_size:
                        img_links = [
                            x.find_element_by_css_selector("img").get_attribute("src")  # noqa: E501
                            for x in elements
                        ]
                        print(img_links.text)
                    else:
                        links = []
                        for friend in results:
                            try:
                                time.sleep(randint(tsmin, tsmax))
                                driver.get(friend)
                                WebDriverWait(driver, 30).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH, selectors.get(
                                            "profilePicThumb"))
                                    )
                                )
                                profile_thumbnail = driver.find_element_by_xpath(    # noqa: E501
                                    selectors.get("profilePicThumb"))
                                ld = driver.find_element_by_css_selector(
                                    "#u_0_2_No").above(
                                    profile_thumbnail).get_attribute("href")
                                driver.get_facebook_images_url
                            except Exception:
                                ld = "None"

                            links.append(ld)

                        for i, _ in enumerate(links):
                            if links[i] is None:
                                links[i] = "None"
                            elif links[i].find("picture/view") != -1:
                                links[i] = "None"

                        img_links = get_facebook_images_url(links)
                        print(img_links.text)

                    folder_names = "Friends_Photos"
                    # folder_names = [
                    #     "Friend's Photos",
                    #     "Mutual Friends' Photos",
                    #     "Following's Photos",
                    #     "Follower's Photos",
                    #     "Work Friends Photos",
                    #     "High School Friends Photos",
                    #     "College Friends Photos",
                    #     "Current City Friends Photos",
                    #     "Hometown Friends Photos",
                    # ]
                    print("Downloading " + folder_names[current_section])

                    img_names = image_downloader(
                        img_links, folder_names[current_section]
                    )
                    print(img_names.text)
                else:
                    img_names = ["None"] * len(results)
            except Exception:
                print(
                    "Exception (Images)",
                    str(status),
                    "Status =",
                    current_section,
                    sys.exc_info()[0],
                )

### Handling Photo Links

# ****************************************************************************
# *                               Handle Photos                              *
# ****************************************************************************

        elif status == 1:
            results = [x.get_attribute("href") for x in elements]
            results.pop(0)

            try:
                if download_uploaded_photos:
                    if photos_small_size:
                        background_img_links = driver.find_elements_by_xpath(
                            selectors.get("background_img_links")
                        )
                        background_img_links = [
                            x.get_attribute(
                                "style") for x in background_img_links
                        ]
                        background_img_links = [
                            ((x.split("(")[1]).split(")")[0]).strip('"')
                            for x in background_img_links
                        ]
                    else:
                        background_img_links = get_facebook_images_url(results)

                    folder_names = ["Uploaded Photos", "Tagged Photos"]
                    print("Downloading " + folder_names[current_section])

                    img_names = image_downloader(
                        background_img_links, folder_names[current_section]
                    )
                else:
                    img_names = ["None"] * len(results)
            except Exception:
                print(
                    "Exception (Images)",
                    str(status),
                    "Status =",
                    current_section,
                    sys.exc_info()[0],
                )
# ****************************************************************************
# *                               Handle About:                              *
# ****************************************************************************
        # dealing with About Section
        # elif status == 3:
        #     results = elements[0].text
        #     f.writelines(results)

### Write results to file

# ****************************************************************************
# *                               Write to file                              *
# ****************************************************************************

        """Write results to file"""
        if status == 0:
            for i, _ in enumerate(results):
                # friend's profile link
                f.writelines(results[i])
                f.write(",")

                # friend's name
                f.writelines(people_names[i])
                f.write(",")

                # friend's downloaded picture id
                f.writelines(img_names[i])
                f.write("\n")

        elif status == 1:
            for i, _ in enumerate(results):
                # image's link
                f.writelines(results[i])
                f.write(",")

                # downloaded picture id
                f.writelines(img_names[i])
                f.write("\n")

        elif status == 2:
            for x in results:
                f.writelines(x + "\n")

        f.close()

    except Exception:
        print("Exception (save_to_file)", "Status =", str(status), sys.exc_info()[0])  # noqa: E501

    return


# ## Defining the scraping process

# In[ ]:


# -----------------------------------------------------------------------------
# ****************************************************************************
# *                          Defines scraping process                        *
# ****************************************************************************
# -----------------------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scrape_data(user_id, scan_list, section, elements_path, save_status, file_names):  # noqa: E501
    """Given some parameters, this function can scrape
    friends/photos/videos/about/posts(statuses) of a profile"""
    page = []

    if save_status == 4:
        page.append(user_id)

    page += [user_id + s for s in section]

    for i, _ in enumerate(scan_list):
        try:
            time.sleep(randint(tsmin, tsmax))
            driver.get(page[i])

            if (
                (save_status == 0) or (save_status == 1) or (save_status == 2)
            ):  # Only run this for friends, photos and videos

                # the bar which contains all the sections
                sections_bar = driver.find_element_by_xpath(
                    selectors.get("sections_bar")
                )

                if sections_bar.text.find(scan_list[i]) == -1:
                    continue

            if save_status != 3:
                utils.scroll(total_scrolls, driver, selectors, scroll_time)

            data = driver.find_elements_by_xpath(elements_path[i])

            save_to_file(file_names[i], data, save_status, i)

        except Exception:
            print(
                "Exception (scrape_data)",
                str(i),
                "Status =",
                str(save_status),
                sys.exc_info()[0],
            )


## Create original link

# In[ ]:


# -----------------------------------------------------------------------------
#####################################################
#      ___       _           _     _       _        #
#     / _ \ _ __(_) __ _    | |   (_)_ __ | | __    #
#    | | | | '__| |/ _` |   | |   | | '_ \| |/ /    #
#    | |_| | |  | | (_| |_  | |___| | | | |   <     #
#     \___/|_|  |_|\__, (_) |_____|_|_| |_|_|\_\    #
#                  |___/                            #
#####################################################
# -----------------------------------------------------------------------------
# DONE:


def create_original_link(url):
    if url.find(".php") != -1:
        original_link = (
            facebook_https_prefix + facebook_link_body + ((url.split("="))[1])
        )

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + ((url.split("/"))[-1].split("?")[0])
        )
    elif url.find("_tab") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + (url.split("?")[0]).split("/")[-1]
        )
    else:
        original_link = url

    return original_link


# ## Read and Run

# In[ ]:


# -----------------------------------------------------------------------------

#  ___             _   ___                _     __       ___
# | _ \___ __ _ __| | |_ _|_ _  _ __ _  _| |_  / _|___  | _ \_  _ _ _
# |   / -_) _` / _` |  | || ' \| '_ \ || |  _| > _|_ _| |   / || | ' \
# |_|_\___\__,_\__,_| |___|_||_| .__/\_,_|\__| \_____|  |_|_\\_,_|_||_|
#                              |_|

# -----------------------------------------------------------------------------
def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


# In[ ]:


# ****************************************************************************
# *                       Start scraping profiles Here                       *
# ****************************************************************************


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scrap_profile(ids):
    folder = os.path.join(os.getcwd(), "data")
    utils.create_folder(folder)
    os.chdir(folder)

    # execute for all profiles given in input.txt file
    for user_id in ids:

        time.sleep(randint(tsmin, tsmax))
        # block_check()
        driver.get(user_id)
        url = driver.current_url
        user_id = create_original_link(url)
        print(url)
        print("\nScraping:", user_id)

        try:
            target_dir = os.path.join(folder, user_id.split("/")[-1])
            utils.create_folder(target_dir)
            os.chdir(target_dir)
        except Exception:
            print("Some error occurred in creating the profile directory.")
            continue

        # to_scrap = ["Friends", "Photos", "Videos", "About", "Posts"]
        to_scrap = ["Friends", "Photos"]
        for item in to_scrap:
            print(to_scrap)
            print("----------------------------------------")
            print("Scraping {}..".format(item))

            # if item == "Posts":
            #     scan_list = [None]
            # elif item == "About":
            #     scan_list = [None] * 7
            # else:
            #     scan_list = params[item]["scan_list"]

            # if item == "About":
            #     scan_list == [None] * 7
            # else:
            #     scan_list = params[item]["scan_list"]

        scan_list = params[item]["scan_list"]
        section = params[item]["section"]
        elements_path = params[item]["elements_path"]
        file_names = params[item]["file_names"]
        save_status = params[item]["save_status"]

        scrape_data(
            user_id, scan_list, section, elements_path, save_status, file_names
        )

        print("{} Done!".format(item))

    print("\nProcess Completed.")
    os.chdir("../..")

    return


# ## Login

# In[ ]:


# -----------------------------------------------------------------------------

############################################################
#     _                      _               ___           #
#    | |    ___   __ _  __ _(_)_ __   __ _  |_ _|_ __      #
#    | |   / _ \ / _` |/ _` | | '_ \ / _` |  | || '_ \     #
#    | |__| (_) | (_| | (_| | | | | | (_| |  | || | | |    #
#    |_____\___/ \__, |\__, |_|_| |_|\__, | |___|_| |_|    #
#                |___/ |___/         |___/                 #
############################################################

# -----------------------------------------------------------------------------


def safe_find_element_by_id(driver, elem_id):
    try:
        return driver.find_element_by_id(elem_id)
    except NoSuchElementException:
        return None


def login(email, password):
    """ Logging into our own profile """

    try:
        global driver

        # I believe below is what is causing the script to open two browsers.
        # -------------------------------------------------------------
        # opts = Options()

        # #  Code to disable notifications pop up of Firefox Browser
        # opts.add_argument("--disable-notifications")
        # opts.add_argument("--disable-infobars")
        # opts.add_argument("--mute-audio")
        # opts.add_argument("--no-sandbox")
        # opts.add_argument("headless")

        try:
            platform_ = platform.system().lower()
#             driver = webdriver.Firefox(
#                 executable_path="/usr/local/bin/geckodriver"
#             )

        except Exception:
            print(
                "Kindly replace the Firefox Web Driver with the latest one from "  # noqa: E501
                "http://geckodriver.chromium.org/downloads "
                "and also make sure you have the latest Firefox Browser version."  # noqa: E501
                "\nYour OS: {}".format(platform_)
            )
            exit(1)

        fb_path = facebook_https_prefix + facebook_link_body
        driver.get(fb_path)
        driver.maximize_window()

        # filling the form
        driver.find_element_by_name("email").send_keys(email)
        driver.find_element_by_name("pass").send_keys(password)

        # Facebook new design
        driver.find_element_by_xpath("//input[@value='Log In']").click()
        # driver.implicitly_wait(driver, 20).until(EC.presence_of_element_located(By.XPATH, selectors.get("not_Now")))  # noqa: E501
        WebDriverWait(driver, 20)
        driver.find_element_by_xpath(selectors.get("notNow")).click()
        # if presence_of_element_located(By.XPATH, selectors.get("not_Now")) is True:  # noqa: E501
        #     try:
        #         driver.find_element_by_xpath(selectors.get("not_Now")).click()  # noqa: E501
        #     except Exception:
        #         print("Something fishing is going on here.")
        #         exit(0)

    except Exception:
        print("There is something wrong with logging in.")
        print(sys.exc_info()[0])
        exit(0)

# ****************************************************************************
# *                           Multi Factor handling                          *
# ****************************************************************************

        # if your account uses multi factor authentication
        # mfa_code_input = safe_find_element_by_id(driver, "approvals_code")

        # if mfa_code_input is None:
        #     return

        # mfa_code_input.send_keys(input("Enter MFA code: "))
        # driver.find_element_by_id("checkpointSubmitButton").click()

        # # there are so many screens asking you to verify things.
        # Just skip them all
        # while safe_find_element_by_id(driver,
        # "checkpointSubmitButton") is not None:
        #     dont_save_browser_radio =
        #     safe_find_element_by_id(driver, "u_0_3")
        #     if dont_save_browser_radio is not None:
        #         dont_save_browser_radio.click()

        #     driver.find_element_by_id("checkpointSubmitButton").click()

#     except Exception:
#         print("There's some error in log in.")
#         print(sys.exc_info()[0])
#         exit(1)


# ## CLI Errors

# In[ ]:


# -----------------------------------------------------------------------------
'''
######  ##       ####
##    ## ##        ##
##       ##        ##
##       ##        ##
##       ##        ##
##    ## ##        ##
######  ######## ####

######## ########  ########   #######  ########
##       ##     ## ##     ## ##     ## ##     ##
##       ##     ## ##     ## ##     ## ##     ##
######   ########  ########  ##     ## ########
##       ##   ##   ##   ##   ##     ## ##   ##
##       ##    ##  ##    ##  ##     ## ##    ##
######## ##     ## ##     ##  #######  ##     ##
'''
# -----------------------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scraper(**kwargs):
    with open("credentials.yaml", "r") as ymlfile:
        cfg = yaml.safe_load(stream=ymlfile)

    if ("password" not in cfg) or ("email" not in cfg):
        print(
            "Your email or password is missing. Kindly write them in credentials.txt"
        )
        exit(1)

    ids = [
        facebook_https_prefix + facebook_link_body + line.split("/")[-1]
        for line in open("input.txt", newline="\n")
    ]

    if len(ids) > 0:
        print("\nStarting Scraping...")

        login(cfg["email"], cfg["password"])
        scrap_profile(ids)
        driver.close()
    else:
        print("Input file is empty.")

## CLI Help

# -------------------------------------------------------------

#####################################################
#      ____ _     ___   _   _ _____ _     ____      #
#     / ___| |   |_ _| | | | | ____| |   |  _ \     #
#    | |   | |    | |  | |_| |  _| | |   | |_) |    #
#    | |___| |___ | |  |  _  | |___| |___|  __/     #
#     \____|_____|___| |_| |_|_____|_____|_|        #
#                                                   #
#####################################################

# -------------------------------------------------------------

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    # PLS CHECK IF HELP CAN BE BETTER / LESS AMBIGUOUS
    ap.add_argument(
        "-dup",
        "--uploaded_photos",
        help="download users' uploaded photos?",
        default=True,
    )
    ap.add_argument(
        "-dfp", "--friends_photos",
        help="download users' photos?", default=True
    )
    ap.add_argument(
        "-fss",
        "--friends_small_size",
        help="Download friends pictures in small size?",
        default=True,
    )
    ap.add_argument(
        "-pss",
        "--photos_small_size",
        help="Download photos in small size?",
        default=True,
    )
    ap.add_argument(
        "-ts",
        "--total_scrolls",
        help="How many times should I scroll down?",
        default=2500,
    )
    ap.add_argument(
        "-st", "--scroll_time",
        help="How much time should I take to scroll?", default=8
    )

    args = vars(ap.parse_args())
    print(args)


# ## More Global Variables

# In[ ]:


# ---------------------------------------------------------

######################################################
#      ____ _       _           _                    #
#     / ___| | ___ | |__   __ _| |                   #
#    | |  _| |/ _ \| '_ \ / _` | |                   #
#    | |_| | | (_) | |_) | (_| | |                   #
#     \____|_|\___/|_.__/ \__,_|_|                   #
#                                                    #
#    __     __         _       _     _               #
#    \ \   / /_ _ _ __(_) __ _| |__ | | ___  ___     #
#     \ \ / / _` | '__| |/ _` | '_ \| |/ _ \/ __|    #
#      \ V / (_| | |  | | (_| | |_) | |  __/\__ \    #
#       \_/ \__,_|_|  |_|\__,_|_.__/|_|\___||___/    #
#                                                    #
######################################################

# ---------------------------------------------------------

# whether to download photos or not
download_uploaded_photos = utils.to_bool(args["uploaded_photos"])
download_friends_photos = utils.to_bool(args["friends_photos"])

# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick else if its false then
# it will open each photo to download it and it will take much more time
#     friends_small_size = utils.to_bool(args["friends_small_size"])
#     photos_small_size = utils.to_bool(args["photos_small_size"])

total_scrolls = int(args["total_scrolls"])
scroll_time = int(args["scroll_time"])

current_scrolls = 0
old_height = 0

with open("selectors.json") as a, open("params.json") as b:
    selectors = json.load(a)
    params = json.load(b)

# firefox_profile_path = selectors.get("firefox_profile_path")
facebook_https_prefix = selectors.get("facebook_https_prefix")
facebook_link_body = selectors.get("facebook_link_body")


# ## RUN!

# In[ ]:


# ****************************************************************************
# *                                    RUN                                   *
# ****************************************************************************

# get things rolling
if __name__ == "__main__":
    scraper()

