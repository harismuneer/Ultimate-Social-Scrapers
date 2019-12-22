import calendar
import os
import platform
import sys
## Custom Imports for time banning.
import time
import urllib.request
from random import randint

import yaml
from ratelimit import limits
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# -------------------------------------------------------------
# -------------------------------------------------------------


# Global Variables
opts = Options()
opts.add_argument(
    "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone10,2;FBMD/iPhone;FBSN/iOS;FBSV/13.1.3;FBSS/3;FBID/phone;FBLC/en_US;FBOP/5;FBCR/Verizon]"
)

# If you change this variable the scraping process will change
# and not all elements will be scraped.
# driver = None
driver = webdriver.Chrome(options=opts)

# whether to download photos or not
download_uploaded_photos = True
download_friends_photos = True

# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick else if its false then it will open each photo to download it
# and it will take much more time
friends_small_size = False
photos_small_size = False

total_scrolls = 2500
current_scrolls = 0
scroll_time = 8

old_height = 0
facebook_https_prefix = "https://"

# Values for rate limiting | lower is slower!
# Last worked at: low=10,high=25,time=600
# Failed at: low=10,high=30
# But, leaving values alone.
rtqlow = 10
rtqhigh = 30
rtime = 600

# Traversal speed is solely controlled by this variable
# Vales for time sleep in secs
# Last worked at: min=25,max=40
# Failed at: min=20, max=40
tsmin = 25
tsmax = 55

CHROMEDRIVER_BINARIES_FOLDER = "bin"


# -------------------------------------------------------------
# Identify Image Links
# Important Note! The script scans the profiles and appends the
# links to a list, then downloads them later.
# -------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=rtime)
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
                        EC.presence_of_element_located((By.CLASS_NAME, "spotlight"))
                    )
                    element = driver.find_element_by_class_name("spotlight")
                    img_url = element.get_attribute("src")

                    if img_url.find(".gif") == -1:
                        valid_url_found = True
                        urls.append(img_url)
            except Exception:
                urls.append("None")
        else:
            urls.append("None")

    return urls


# -------------------------------------------------------------
# Image Downloader
# -------------------------------------------------------------

# takes a url and downloads image from that url
@limits(calls=randint(rtqlow, rtqhigh), period=rtime)
def image_downloader(img_links, folder_name):
    img_names = []

    try:
        parent = os.getcwd()
        try:
            folder = os.path.join(os.getcwd(), folder_name)
            create_folder(folder)
            os.chdir(folder)
        except Exception:
            print("Error in changing directory.")

        for link in img_links:
            img_name = "None"

            if link != "None":
                img_name = (link.split(".jpg")[0]).split("/")[-1] + ".jpg"

                # this is the image id when there's no profile pic
                if img_name == "10354686_10150004552801856_220367501106153455_n.jpg":
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


def check_height():
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height


# -------------------------------------------------------------
# -------------------------------------------------------------

# helper function: used to scroll the page
def scroll():
    global old_height
    current_scrolls = 0

    while True:
        try:
            if current_scrolls == total_scrolls:
                return

            old_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.05).until(
                lambda driver: check_height()
            )
            current_scrolls += 1
        except TimeoutException:
            break

    return


# -------------------------------------------------------------
# -------------------------------------------------------------

# --Helper Functions for Posts


def get_status(x):
    status = ""
    try:
        status = x.find_element_by_xpath(
            ".//div[@class='_5wj-']"
        ).text  # use _1xnd for Pages
    except Exception:
        try:
            status = x.find_element_by_xpath(".//div[@class='userContent']").text
        except Exception:
            pass
    return status


def get_div_links(x, tag):
    try:
        temp = x.find_element_by_xpath(".//div[@class='_3x-2']")
        return temp.find_element_by_tag_name(tag)
    except Exception:
        return ""


def get_title_links(title):
    l = title.find_elements_by_tag_name("a")
    return l[-1].text, l[-1].get_attribute("href")


def get_title(x):
    title = ""
    try:
        title = x.find_element_by_xpath(".//span[@class='fwb fcg']")
    except Exception:
        try:
            title = x.find_element_by_xpath(".//span[@class='fcg']")
        except Exception:
            try:
                title = x.find_element_by_xpath(".//span[@class='fwn fcg']")
            except Exception:
                pass
    finally:
        return title


def get_time(x):
    time = ""
    try:
        time = x.find_element_by_tag_name("abbr").get_attribute("title")
        time = (
                str("%02d" % int(time.split(", ")[1].split()[1]), )
                + "-"
                + str(
            (
                    "%02d"
                    % (
                        int(
                            (
                                list(calendar.month_abbr).index(
                                    time.split(", ")[1].split()[0][:3]
                                )
                            )
                        ),
                    )
            )
        )
                + "-"
                + time.split()[3]
                + " "
                + str("%02d" % int(time.split()[5].split(":")[0]))
                + ":"
                + str(time.split()[5].split(":")[1])
        )
    except Exception:
        pass

    finally:
        return time


# Deals with scraping posts
@limits(calls=randint(rtqlow, rtqhigh), period=rtime)
def extract_and_write_posts(elements, filename):
    try:
        f = open(filename, "w", newline="\r\n")
        f.writelines(
            " TIME || TYPE  || TITLE || STATUS  ||   LINKS(Shared Posts/Shared Links etc) "
            + "\n"
            + "\n"
        )

        for x in elements:
            try:
                title = " "
                status = " "
                link = " "
                time = " "

                # time
                time = get_time(x)

                # title
                title = get_title(x)
                if title.text.find("shared a memory") != -1:
                    x = x.find_element_by_xpath(".//div[@class='_1dwg _1w_m']")
                    title = get_title(x)

                status = get_status(x)
                if (
                    title.text
                    == driver.find_element_by_id("fb-timeline-cover-name").text
                ):
                    if status == "":
                        temp = get_div_links(x, "img")
                        if (
                            temp == ""
                        ):  # no image tag which means . it is not a life event
                            link = get_div_links(x, "a").get_attribute("href")
                            type = "status update without text"
                        else:
                            type = "life event"
                            link = get_div_links(x, "a").get_attribute("href")
                            status = get_div_links(x, "a").text
                    else:
                        type = "status update"
                        if get_div_links(x, "a") != "":
                            link = get_div_links(x, "a").get_attribute("href")

                elif title.text.find(" shared ") != -1:

                    x1, link = get_title_links(title)
                    type = "shared " + x1

                elif title.text.find(" at ") != -1 or title.text.find(" in ") != -1:
                    if title.text.find(" at ") != -1:
                        x1, link = get_title_links(title)
                        type = "check in"
                    elif title.text.find(" in ") != 1:
                        status = get_div_links(x, "a").text

                elif (
                    title.text.find(" added ") != -1 and title.text.find("photo") != -1
                ):
                    type = "added photo"
                    link = get_div_links(x, "a").get_attribute("href")

                elif (
                    title.text.find(" added ") != -1 and title.text.find("video") != -1
                ):
                    type = "added video"
                    link = get_div_links(x, "a").get_attribute("href")

                else:
                    type = "others"

                if not isinstance(title, str):
                    title = title.text

                status = status.replace("\n", " ")
                title = title.replace("\n", " ")

                line = (
                    str(time)
                    + " || "
                    + str(type)
                    + " || "
                    + str(title)
                    + " || "
                    + str(status)
                    + " || "
                    + str(link)
                    + "\n"
                )

                try:
                    f.writelines(line)
                except Exception:
                    print("Posts: Could not map encoded characters")
            except Exception:
                pass
        f.close()
    except Exception:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info()[0])

    return


# -------------------------------------------------------------
# -------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=rtime)
def save_to_file(name, elements, status, current_section):
    """helper function used to save links to files"""

    # status 0 = dealing with friends list
    # status 1 = dealing with photos
    # status 2 = dealing with videos
    # status 3 = dealing with about section
    # status 4 = dealing with posts

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
                x.find_element_by_tag_name("img").get_attribute("aria-label")
                for x in elements
            ]

            # download friends' photos
            try:
                if download_friends_photos:
                    if friends_small_size:
                        img_links = [
                            x.find_element_by_css_selector("img").get_attribute("src")
                            for x in elements
                        ]
                    else:
                        links = []
                        for friend in results:
                            try:
                                time.sleep(randint(tsmin, tsmax))
                                driver.get(friend)
                                WebDriverWait(driver, 30).until(
                                    EC.presence_of_element_located(
                                        (By.CLASS_NAME, "profilePicThumb")
                                    )
                                )
                                l = driver.find_element_by_class_name(
                                    "profilePicThumb"
                                ).get_attribute("href")
                            except Exception:
                                l = "None"

                            links.append(l)

                        for i, _ in enumerate(links):
                            if links[i] is None:
                                links[i] = "None"
                            elif links[i].find("picture/view") != -1:
                                links[i] = "None"

                        img_links = get_facebook_images_url(links)

                    folder_names = [
                        "Friend's Photos",
                        "Mutual Friends' Photos",
                        "Following's Photos",
                        "Follower's Photos",
                        "Work Friends Photos",
                        "College Friends Photos",
                        "Current City Friends Photos",
                        "Hometown Friends Photos",
                    ]
                    print("Downloading " + folder_names[current_section])

                    img_names = image_downloader(
                        img_links, folder_names[current_section]
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

        # dealing with Photos
        elif status == 1:
            results = [x.get_attribute("href") for x in elements]
            results.pop(0)

            try:
                if download_uploaded_photos:
                    if photos_small_size:
                        background_img_links = driver.find_elements_by_xpath(
                            "//*[contains(@id, 'pic_')]/div/i"
                        )
                        background_img_links = [
                            x.get_attribute("style") for x in background_img_links
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

        # dealing with Videos
        elif status == 2:
            results = elements[0].find_elements_by_css_selector("li")
            results = [
                x.find_element_by_css_selector("a").get_attribute("href")
                for x in results
            ]

            try:
                if results[0][0] == "/":
                    results = [r.pop(0) for r in results]
                    results = [("https://en-gb.facebook.com/" + x) for x in results]
            except Exception:
                pass

        # dealing with About Section
        elif status == 3:
            results = elements[0].text
            f.writelines(results)

        # dealing with Posts
        elif status == 4:
            extract_and_write_posts(elements, name)
            return

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
        print("Exception (save_to_file)", "Status =", str(status), sys.exc_info()[0])

    return


# ----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=rtime)
def scrape_data(user_id, scan_list, section, elements_path, save_status, file_names):
    """Given some parameters, this function can scrap friends/photos/videos/about/posts(statuses) of a profile"""
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
                    "//*[@class='_3cz'][1]/div[2]/div[1]"
                )

                if sections_bar.text.find(scan_list[i]) == -1:
                    continue

            if save_status != 3:
                scroll()

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


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def create_original_link(url):
    if url.find(".php") != -1:
        original_link = facebook_https_prefix + ".facebook.com/" + ((url.split("="))[1])

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = (
            facebook_https_prefix
            + ".facebook.com/"
            + ((url.split("/"))[-1].split("?")[0])
        )
    elif url.find("_tab") != -1:
        original_link = (
            facebook_https_prefix
            + ".facebook.com/"
            + (url.split("?")[0]).split("/")[-1]
        )
    else:
        original_link = url

    return original_link


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


@limits(calls=randint(rtqlow, rtqhigh), period=rtime)
def scrap_profile(ids):
    folder = os.path.join(os.getcwd(), "data")
    create_folder(folder)
    os.chdir(folder)

    # execute for all profiles given in input.txt file
    for user_id in ids:

        time.sleep(randint(tsmin, tsmax))
        driver.get(user_id)
        url = driver.current_url
        user_id = create_original_link(url)

        print("\nScraping:", user_id)

        try:
            target_dir = os.path.join(folder, user_id.split("/")[-1])
            create_folder(target_dir)
            os.chdir(target_dir)
        except Exception:
            print("Some error occurred in creating the profile directory.")
            continue

        # ----------------------------------------------------------------------------
        # This section outlines the process in which the scraping will occur.
        # In the following order: 1) Friends, 2) Photos, 3) Videos, 4) About
        # ----------------------------------------------------------------------------
        print("----------------------------------------")
        print("Friends..")
        # setting parameters for scrape_data() to scrape friends
        scan_list = [
            "All",
            "Mutual Friends",
            "Following",
            "Followers",
            "Work",
            "College",
            "Current City",
            "Hometown",
        ]
        section = [
            "/friends",
            "/friends_mutual",
            "/following",
            "/followers",
            "/friends_work",
            "/friends_college",
            "/friends_current_city",
            "/friends_hometown",
        ]
        elements_path = [
            "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
            "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
            "//*[contains(@class,'_3i9')][1]/div/div/ul/li[1]/div[2]/div/div/div/div/div[2]/ul/li/div/a",
            "//*[contains(@class,'fbProfileBrowserListItem')]/div/a",
            "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
            "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
            "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
            "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
        ]
        file_names = [
            "All Friends.txt",
            "Mutual Friends.txt",
            "Following.txt",
            "Followers.txt",
            "Work Friends.txt",
            "College Friends.txt",
            "Current City Friends.txt",
            "Hometown Friends.txt",
        ]
        save_status = 0

        scrape_data(user_id, scan_list, section, elements_path, save_status, file_names)
        print("Friends Done!")

        # ----------------------------------------------------------------------------

        print("----------------------------------------")
        print("Photos..")
        print("Scraping Links..")
        # setting parameters for scrape_data() to scrap photos
        scan_list = ["'s Photos", "Photos of"]
        section = ["/photos_all", "/photos_of"]
        elements_path = ["//*[contains(@id, 'pic_')]"] * 2
        file_names = ["Uploaded Photos.txt", "Tagged Photos.txt"]
        save_status = 1

        scrape_data(user_id, scan_list, section, elements_path, save_status, file_names)
        print("Photos Done!")

        # ----------------------------------------------------------------------------
        print("----------------------------------------")
        print("Videos:")
        # setting parameters for scrape_data() to scrap videos
        scan_list = ["'s Videos", "Videos of"]
        section = ["/videos_by", "/videos_of"]
        elements_path = [
            "//*[contains(@id, 'pagelet_timeline_app_collection_')]/ul"
        ] * 2
        file_names = ["Uploaded Videos.txt", "Tagged Videos.txt"]
        save_status = 2

        scrape_data(user_id, scan_list, section, elements_path, save_status, file_names)
        print("Videos Done!")
        # ----------------------------------------------------------------------------

        print("----------------------------------------")
        print("About:")
        # setting parameters for scrape_data() to scrap the about section
        scan_list = [None] * 7
        section = [
            "/about?section=overview",
            "/about?section=education",
            "/about?section=living",
            "/about?section=contact-info",
            "/about?section=relationship",
            "/about?section=bio",
            "/about?section=year-overviews",
        ]
        elements_path = [
            "//*[contains(@id, 'pagelet_timeline_app_collection_')]/ul/li/div/div[2]/div/div"
        ] * 7
        file_names = [
            "Overview.txt",
            "Work and Education.txt",
            "Places Lived.txt",
            "Contact and Basic Info.txt",
            "Family and Relationships.txt",
            "Details About.txt",
            "Life Events.txt",
        ]
        save_status = 3

        scrape_data(user_id, scan_list, section, elements_path, save_status, file_names)
        print("About Section Done!")

        # ----------------------------------------------------------------------------
        print("----------------------------------------")
        print("Posts:")
        # setting parameters for scrape_data() to scrap posts
        scan_list = [None]
        section = []
        elements_path = ['//div[@class="_5pcb _4b0l _2q8l"]']

        file_names = ["Posts.txt"]
        save_status = 4

        scrape_data(user_id, scan_list, section, elements_path, save_status, file_names)
        print("Posts(Statuses) Done!")
        print("----------------------------------------")
    # ----------------------------------------------------------------------------

    print("\nProcess Completed.")

    return


# -----------------------------------------------------------------------------
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

        options = Options()

        #  Code to disable notifications pop up of Chrome Browser
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        # options.add_argument("headless")

        try:
            platform_ = platform.system().lower()
            if platform_ in ["linux", "darwin"]:
                driver = webdriver.Chrome(
                    executable_path=os.getenv('HOME') + "/bin/chromedriver", options=opts
                )
            else:
                print(
                    "If you are currently running windows,"
                    "please change to a more secure operating system"
                    "immediately!"
                )
                # driver = webdriver.Chrome(
                #     executable_path="./chromedriver.exe", options=options
                # )

            # chromedriver_versions = {
            #     "linux": os.path.join(
            #         os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_linux64",
            #     ),
            #     "darwin": os.path.join(
            #         os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_mac64",
            #     ),
            #     "windows": os.path.join(
            #         os.getcwd(), CHROMEDRIVER_BINARIES_FOLDER, "chromedriver_win32.exe",
            #     ),
            # }
            #
            # driver = webdriver.Chrome(
            #     executable_path=chromedriver_versions[platform_], options=options
            # )

        except Exception:
            print(
                "Kindly replace the Chrome Web Driver with the latest one from "
                "http://chromedriver.chromium.org/downloads "
                "and also make sure you have the latest Chrome Browser version."
                "\nYour OS: {}".format(platform_)
            )
            exit(1)

        fb_path = facebook_https_prefix + "facebook.com"
        driver.get(fb_path)
        driver.maximize_window()

        # filling the form
        driver.find_element_by_name("email").send_keys(email)
        driver.find_element_by_name("pass").send_keys(password)

        try:
            # clicking on login button
            driver.find_element_by_id("loginbutton").click()
        except NoSuchElementException:
            # Facebook new design
            driver.find_element_by_name("login").click()

        # if your account uses multi factor authentication
        mfa_code_input = safe_find_element_by_id(driver, "approvals_code")

        if mfa_code_input is None:
            return

        mfa_code_input.send_keys(input("Enter MFA code: "))
        driver.find_element_by_id("checkpointSubmitButton").click()

        # there are so many screens asking you to verify things. Just skip them all
        while safe_find_element_by_id(driver, "checkpointSubmitButton") is not None:
            dont_save_browser_radio = safe_find_element_by_id(driver, "u_0_3")
            if dont_save_browser_radio is not None:
                dont_save_browser_radio.click()

            driver.find_element_by_id("checkpointSubmitButton").click()

    except Exception:
        print("There's some error in log in.")
        print(sys.exc_info()[0])
        exit(1)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


@limits(calls=randint(rtqlow, rtqhigh), period=rtime)
def scrapper(**kwargs):
    with open("credentials.yaml", "r") as ymlfile:
        cfg = yaml.safe_load(stream=ymlfile)

    if ("password" not in cfg) or ("email" not in cfg):
        print("Your email or password is missing. Kindly write them in credentials.txt")
        exit(1)

    ids = [
        facebook_https_prefix + "facebook.com/" + line.split("/")[-1]
        for line in open("input.txt", newline="\n")
    ]

    if len(ids) > 0:
        print("\nStarting Scraping...")

        login(cfg["email"], cfg["password"])
        scrap_profile(ids)
        driver.close()
    else:
        print("Input file is empty.")


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------

if __name__ == "__main__":
    # get things rolling
    scrapper()
