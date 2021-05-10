#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import os
import platform
import sys

# Custom Imports for time banning.
import time
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
opts.add_argument("--headless")
opts.add_argument("--no-sandbox")
opts.add_argument("--lang=en-US")
opts.add_argument("--dns-prefetch-disable")
# opts.add_argument("--start-maximized")

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
facebook_link_body = "mbasic.facebook.com/"

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

# For gender scraping | Binary only, either "Male" or "Female"
desired_gender = "Female"

# CHROMEDRIVER_BINARIES_FOLDER = "bin"
Firefox(executable_path="/usr/local/bin/geckodriver")


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
    full_Size_Url = driver.find_element_by_xpath("//div[2]/div/div[1]/div/div/div[3]/div[1]/div[2]/span/div/span/a[1]").get_attribute("href")  # noqa: E501
    driver.get(full_Size_Url)
    time.sleep(3)
    image_number = str(randint(1, 9999))
    image_name = "photo" + image_number + ".jpg"
    img_url = driver.current_url
    with requests.get(img_url, stream=True, allow_redirects=True) as r:  # noqa: E501
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
    elif os.path.exists("/tmp/album_image_url.txt"):
        os.remove("/tmps/album_image_url.txt")
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


def get_profile_photos(ids):
    time.sleep(randint(tsmin, tsmax))
    for user_id in ids:
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
                int_fb_id = f1.args.popvalue('owner_id')
                account_id = int_fb_id.strip()
                f2 = furl(photos_url)
                userid_path = str(f2.path)
                userid = userid_path.strip('/')
                back_album_url = "albums/?owner_id="
                album_page_url = facebook_https_prefix + facebook_link_body + userid + "/" + back_album_url + account_id  # noqa: E501
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
                    print("No more albums found")
                    clean_file_sets()
            except Exception:
                print("Unable to generate album page or find any albums")
        except NoSuchElementException:
            print("Fuck!! No Photos Found!")
            clean_file_sets()

# ****************************************************************************
# *                               Friend Walker                              *
# ****************************************************************************


def friend_walker():
    fi_url = driver.current_url
    ff = furl(fi_url)
    f_idl = str(ff.path)
    f_id = f_idl.strip("/friends")
    friend_list = driver.find_elements_by_xpath("//div[2]/div/div/div[2]/div/table/tbody/tr/td[2]/a")  # noqa: E501
    for x in friend_list:
        friend_url = x.get_attribute("href")
        friend_name = x.text
        friend_file = f_id + "friends" + ".txt"
        u = open(friend_file, "a", encoding="utf-8", newline="\n")
        u.writelines(friend_name)
        u.write("\t")
        u.writelines(friend_url)
        u.write("\n")
        u.close()
        friend_url_file = "friend_urls.txt"
        k = open(friend_url_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
        k.writelines(friend_url)
        k.write("\n")
        k.close()

# -------------------------------------------------------------
# ****************************************************************************
# *                                Get Friends                               *
# ****************************************************************************
# -------------------------------------------------------------
# DONE: create a variable that is user_id and friends_id combined for images
# DONE: Add a loop with a limitation of redundancy


def get_friends(ids):
    for user_id in ids:
        driver.get(user_id)
        print("Getting friends of " + user_id)
        try:
            friend_page = driver.find_element_by_xpath("//div[2]/div/div/div/div[4]/a[2]").get_attribute("href")  # noqa: E501
            driver.get(friend_page)
            print("Getting " + friend_page)
            scroll()
            friend_walker()
            friend_list_end = False
            while friend_list_end is False:
                try:
                    # more_friends = driver.find_element_by_xpath('//body[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[3]/a[1]').get_attribute('href') # noqa E501
                    # driver.get(more_friends)
                    driver.find_element_by_xpath('//span[text()="See More Friends"]').click()  # noqa: E501
                    scroll()
                    friend_walker()
                except NoSuchElementException:
                    print("Did not find more friends")
                    friend_list_end = True
        except NoSuchElementException:
            print("Did not find any friends")
            friend_list_end = True

# ****************************************************************************
# *                                Get Gender                                *
# ****************************************************************************


def friend_gender_scraper(ids):
    for user_id in ids:
        if os.path.exists("friend_urls.txt"):
            with open("friend_urls.txt") as ofile:
                for line in ofile:
                    friend_url = line
                    driver.get(friend_url)
                    print('Scraping Gender' + str(friend_url))
                    try:
                        gender = driver.find_element_by_xpath("//div[2]/div/div[1]/div[6]/div/div/div[1]/table/tbody/tr/td[2]/div").text  # noqa: E501
                        print(gender)
                        if gender == desired_gender:
                            friend_scrape_file = "friends_to_scrape.txt"
                            b = open(friend_scrape_file, "a", encoding="utf-8", newline="\n")  # noqa: E501
                            b.writelines(friend_url)
                            b.write("\n")
                            b.close()
                            with open("friends_to_scrape.txt") as ids:
                                get_profile_photos(ids)
                                get_friends(ids)
                    except NoSuchElementException:
                        print("No Gender Found")
        else:
            print("File does not exist")


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
        clean_file_sets()
        get_profile_photos(ids)
        get_friends(ids)
        friend_gender_scraper(ids)

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
        driver.find_element_by_xpath("//body[1]/div[1]/div[1]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/div[1]/div[3]/a[1]").click()  # noqa: E501

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

# ## RUN!

# In[ ]:


# ****************************************************************************
# *                                    RUN                                   *
# ****************************************************************************

# get things rolling
if __name__ == "__main__":
    scraper()
