#!/usr/bin/env python
# coding: utf-8

# ----------------------------------------------------------------------------
# Copyright (c) 2021 anoduck

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------------
# Jeezus this code is a fucking mess...

import requests
import shutil
import argparse
import json
import os
import platform
import sys

# Custom Imports for time banning.
import time
import urllib.request
# from urllib.request import urlopen, Request
from random import randint
from furl import furl

import utils
import yaml
# import seleniumsupport
from ratelimit import limits
from selenium import webdriver
# from selenium_stealth import stealth
from selenium.webdriver import Firefox
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

# For requests library
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}  # noqa: E501

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
scroll_time = 20

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


# ****************************************************************************
# *                              id control                                  *
# ****************************************************************************

def scraper_control():
    global p_ids
    global friend_ids
    current_dir = os.getcwd()
    print(current_dir)
    in_file = open("../../../input.txt", newline="\n")
    idents = in_file.readlines()
    for line in idents:
        user_ident = line
        dir_prefix = "../../../"
        friend_url_filePath = dir_prefix + "data/" + user_ident + "/" + "friend_urls.txt"  # noqa: E501
        if os.path.exists(friend_url_filePath):
            friend_ids = [
                line.split("/")[-1]
                for line in open("friend_urls.txt", newline="\n")
            ]

            if len(friend_ids) > 0:
                print("\nStarting Scraping Friend photos...")

                gender = get_gender(friend_ids)
                if gender == "female":
                    p_ids = friend_ids

            else:
                global scrape_complete
                scrape_complete = True
        else:
            p_ids = ids


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


# ---------------------------------------------------------
###################################################################
#      ___      _ _               __      __    _ _               #
#     / __|__ _| | |___ _ _ _  _  \ \    / /_ _| | |_____ _ _     #
#    | (_ / _` | | / -_) '_| || |  \ \/\/ / _` | | / / -_) '_|    #
#     \___\__,_|_|_\___|_|  \_, |   \_/\_/\__,_|_|_\_\___|_|      #
#                           |__/                                  #
###################################################################
# ----------------------------------------------------------

def gallery_walker():
    phset = False
    while phset is False:
        photos_links = driver.find_elements_by_xpath("//td/div/a")  # noqa: E501
        for i in photos_links:
            image_link = i.get_attribute("href")
            q = open("/tmp/image_url.txt", "a", encoding="utf-8", newline="\n")  # noqa: E501
            q.writelines(image_link)
            q.write("\n")
            q.close()
        try:
            gallery_set = driver.find_element_by_xpath("//table/tbody/tr/td/div/span/div/a").get_attribute("href")  # noqa: E501
            print("Trying next page...")
            driver.get(gallery_set)
        except NoSuchElementException:
            print("reached end of set")
            phset = True
            print("Downing scraped photos")
            with open("/tmp/image_url.txt") as rfile:
                for line in rfile:
                    driver.get(line)
                    get_fullphoto()
            if os.path.exists("/tmp/image_url.txt"):
                print("Cleaning...")
                os.remove("/tmp/image_url.txt")
            else:
                print("The file does not exist")


################################################################
#       _   _ _                __      __    _ _               #
#      /_\ | | |__ _  _ _ __   \ \    / /_ _| | |_____ _ _     #
#     / _ \| | '_ \ || | '  \   \ \/\/ / _` | | / / -_) '_|    #
#    /_/ \_\_|_.__/\_,_|_|_|_|   \_/\_/\__,_|_|_\_\___|_|      #
#                                                              #
################################################################

def album_walker():
    print("Walking the album")
    alset = False
    while alset is False:
        album_photos_links = driver.find_elements_by_xpath("//article/div/section/div/a")  # noqa: E501
        print("Writing Image links...")
        for s in album_photos_links:
            album_image_link = s.get_attribute("href")
            v = open("/tmp/album_image_url.txt", "a", encoding="utf-8", newline="\n")  # noqa: E501
            v.writelines(album_image_link)
            v.write("\n")
            v.close()
        try:
            album_nextpage = driver.find_element_by_xpath("//article/div/div/div/a").get_attribute("href")  # noqa: E501
            driver.get(album_nextpage)
            print("Trying next page in album...")
        except NoSuchElementException:
            print("Downing scraped photos")
            with open("/tmp/album_image_url.txt") as ai_file:
                for line in ai_file:
                    driver.get(line)
                    print("Getting  " + line)
                    get_fullphoto()
            alset = True
    if alset is True:
        print("Cleaning...")
        if os.path.exists("/tmp/album_image_url.txt"):
            os.remove("/tmp/album_image_url.txt")
        else:
            print("The file does not exist")


# --------------------------------------------------------
###############################################################
#              _      __      _ _        _        _           #
#     __ _ ___| |_   / _|_  _| | |  _ __| |_  ___| |_ ___     #
#    / _` / -_)  _| |  _| || | | | | '_ \ ' \/ _ \  _/ _ \    #
#    \__, \___|\__| |_|  \_,_|_|_| | .__/_||_\___/\__\___/    #
#    |___/                         |_|                        #
###############################################################
# ---------------------------------------------------------


def get_fullphoto():
    full_Size_Url = driver.find_element_by_xpath(
        "//a[text()='View Full Size']").get_attribute("href")
    image_number = str(randint(1, 9999))
    image_name = "photo" + image_number + ".jpg"
    with requests.get(full_Size_Url, stream=True, allow_redirects=True) as r:  # noqa: E501
        with open(image_name, "wb") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


# ****************************************************************************
# *                              Clean File Sets                             *
# ****************************************************************************

def clean_file_sets():
    if os.path.exists("/tmp/album_url.txt"):
        os.remove("/tmp/album_url.txt")
    elif os.path.exists("/tmp/image_url.txt"):
        os.remove("/tmp/image_url.txt")
    else:
        print("Set files do not exist")


# ---------------------------------------------------------

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
# DONE: prevent infinite loop of scraping photos.


def get_profile_photos(p_ids):
    time.sleep(randint(tsmin, tsmax))
    for user_id in p_ids:
        # profile_imgs = []
        driver.get(user_id)
        url = driver.current_url
        user_id = create_original_link(url)
        render_phrase = 'Scraping photos =  ' + str(user_id)
        print(render_phrase)
        try:
            WebDriverWait(driver, 5)
            photos_url = driver.find_element_by_xpath("//a[text()='Photos']").get_attribute("href")  # noqa: E501
            driver.get(photos_url)
            photos_view = driver.find_elements_by_xpath("//section/a")
            for j in photos_view:
                pv_link = j.get_attribute("href")
                driver.get(pv_link)
                gallery_walker()
            try:
                print("Generating albums page...")
                f1 = furl(pv_link)
                prefix = "https://"
                int_fb_id = f1.args.popvalue('owner_id')
                account_id = int_fb_id.strip()
                f2 = furl(photos_url)
                userid_path = str(f2.path)
                userid = userid_path.strip('/')
                front_album_url = "mbasic.facebook.com"
                back_album_url = "albums/?owner_id="
                album_page_url = prefix + front_album_url + "/" + userid + "/" + back_album_url + account_id  # noqa: E501
                print(album_page_url)
                driver.get(album_page_url)
                try:
                    photo_albums_links = driver.find_elements_by_xpath("//span/a")  # noqa: E501
                    for bb in photo_albums_links:
                        album_link = bb.get_attribute("href")
                        print("Opening  " + album_link)
                        k = open("/tmp/album_url.txt", "a", encoding="utf-8", newline="\n")  # noqa: E501
                        k.writelines(album_link)
                        k.write("\n")
                        k.close()
                        with open("/tmp/album_url.txt") as kfile:
                            for line in kfile:
                                driver.get(line)
                                print("Opening album  " + line)
                                album_walker()
                        print("Cleaning...")
                        if os.path.exists("/tmp/album_url.txt"):
                            os.remove("/tmp/album_url.txt")
                        else:
                            print("The file does not exist")
                except NoSuchElementException:
                    print("No album page found")
                    clean_file_sets()
            except Exception:
                print("Unable to generate album page or find any albums")
                clean_file_sets()
        except NoSuchElementException:
            print("Fuck!! No Photos Found!")

# ## Image Downloader

# In[116]:

# -------------------------------------------------------------
# ****************************************************************************
# *                                Get Friends                               *
# ****************************************************************************
# -------------------------------------------------------------
# DONE: create a variable that is user_id and friends_id combined for images
# DONE: Add a loop with a limitation of redundancy


def get_friends(p_ids):
    for user_id in p_ids:
        driver.get(user_id)
        try:
            driver.find_element_by_xpath("//body[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/a[3]").click()  # noqa: E501
            global profile_name
            profile_name = driver.find_elements_by_xpath("//body[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]/strong[1]").text  # noqa: E501
            friend_box = driver.find_element_by_xpath("//body[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]")  # noqa: E501
            friend_list = friend_box.find_elements_by_xpath("//a[@class='cf']")
            for x in friend_list:
                friend_url = x.get_attribute("href")
                friend_name = x.get_attribute("text")
                friend_file = user_id + "friends" + ".txt"
                u = open(friend_file, "w", encoding="utf-8", newline="\n")
                for i, _ in enumerate(friend_name):
                    u.writelines(friend_name[i])
                    u.write("\t")
                    u.writelines(friend_url[i])
                    u.write("\n")
                global friend_url_file
                friend_url_file = "friend_urls.txt"
                k = open(friend_url_file, "w", encoding="utf-8", newline="\n")  # noqa: E501
                for k, _ in enumerate(friend_url):
                    k.writelines(friend_url[k])
                    u.write("\n")
            friend_list_end = False
            while friend_list_end is False:
                try:
                    driver.find_element_by_xpath("//span[text()='See More Friends']").click() # noqa E501
                    driver.friend_list()
                    for x in friend_list:
                        friend_url = x.get_attribute("href")
                        friend_name = x.get_attribute("text")
                        friend_file = user_id + "friends" + ".txt"
                        u = open(friend_file, "w", encoding="utf-8", newline="\n")  # noqa: E501
                        for i, _ in enumerate(friend_name):
                            u.writelines(friend_name[i])
                            u.write("\t")
                            u.writelines(friend_url[i])
                            u.write("\n")
                        # friend_url_file = profile_name + "friend_urls" + ".txt"  # noqa: E501
                        k = open(friend_url_file, "w", encoding="utf-8", newline="\n")  # noqa: E501
                        for k, _ in enumerate(friend_url):
                            k.writelines(friend_url[k])
                            u.write("\n")
                except NoSuchElementException:
                    friend_list_end = True
                    print("Did not find any more friends.")
                    scraped_friends = "done"
        except NoSuchElementException:
            print("Friends Element Not Found")
            scraped_friends = "done"
            return scraped_friends

# ****************************************************************************
# *                                Get Gender                                *
# ****************************************************************************


def get_gender(friend_ids):
    for user_id in friend_ids:
        # profile_imgs = []
        driver.get(user_id)
        print('Scraping Gender' + str(user_id))
        try:
            find_gender = driver.find_elements_by_xpath("//span[@innerstringmarker='Gender']")  # noqa: E501
            if NoSuchElementException is False:
                gender_label = find_gender.to_right_of(find_gender)  # noqa: E501
                gender = gender_label.text
                print(gender)
                if gender == "Female":
                    continue
                else:
                    break
        except NoSuchElementException:
            print("No Gender Found")
            continue


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
    img_link = []
    img_link = driver.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
    img_links = img_link.append(img_links)

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
def save_to_file(name, elements, status, friends_urls, current_section):
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

# Handling Photo Links

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
# *                               Write to file                              *
# ****************************************************************************

        """Write results to file"""
        if status == 0:
            for i, _ in enumerate(results):
                # friend's profile link
                f.writelines(results[i])
                f.write(",")

                # friend's name
                # f.writelines(friend_names[i])
                # f.write("\n")

                # people's name
                f.writelines(people_names[i])
                f.write("\n")

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


##########################################################################
#     ___                          _   _         _        _    _ _       #
#    / __| __ _ _ __ _ _ __  ___  | |_| |_  __ _| |_   __| |_ (_) |_     #
#    \__ \/ _| '_/ _` | '_ \/ -_) |  _| ' \/ _` |  _| (_-< ' \| |  _|    #
#    |___/\__|_| \__,_| .__/\___|  \__|_||_\__,_|\__| /__/_||_|_|\__|    #
#                     |_|                                                #
##########################################################################


# ****************************************************************************
# *                       Start scraping profiles Here                       *
# ****************************************************************************

# ****************************************************************************
# *                               Main function                              *
# ****************************************************************************


@limits(calls=randint(rtqlow, rtqhigh), period=randint(rltime, rhtime))
def scrap_profile(ids):
    folder = os.path.join(os.getcwd(), "data")
    utils.create_folder(folder)
    os.chdir(folder)

    # execute for all profiles given in input.txt file
    for user_id in ids:

        time.sleep(randint(tsmin, tsmax))
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

        # This defines what gets scraped
        # -------------------------------
        global scrape_complete
        scrape_complete = False
        while scrape_complete is False:
            scraper_control()
            get_profile_photos(p_ids)
            get_friends(p_ids)

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

        try:
            platform_ = platform.system().lower()

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
        WebDriverWait(driver, 7)
        driver.find_element_by_xpath(selectors.get("notNow")).click()

    except Exception:
        print("There is something wrong with logging in.")
        print(sys.exc_info()[0])
        exit(0)

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
            "Your email or password is missing. Kindly write them in credentials.txt"  # noqa: E501
        )
        exit(1)

    global ids
    ids = [
        facebook_https_prefix + facebook_link_body + line.split("/")[-1]
        for line in open("input.txt", newline="\n")
    ]

    if len(ids) > 0:
        print("\nStarting Scraping...")

        login(cfg["email"], cfg["password"])
        scrap_profile(ids)
        # driver.close() # -> Suspect of creating two browser windows
    else:
        print("Input file is empty.")


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
# Does not work any longer | will remove in the future
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
