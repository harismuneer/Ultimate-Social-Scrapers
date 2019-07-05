import calendar
import sys
import urllib.request
import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# -------------------------------------------------------------
# -------------------------------------------------------------


# Global Variables

# whether to download photos or not
download_uploaded_photos = True
download_friends_photos = True

# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick else if its false then it will open each photo to download it
# and it will take much more time
friends_small_size = True
photos_small_size = True

total_scrolls = 2500
current_scrolls = 0
scroll_time = 8

old_height = 0

facebook_https_prefix = "https://"


# -------------------------------------------------------------
# -------------------------------------------------------------

def get_facebook_images_url(driver, img_links):
    urls = []

    for link in img_links:
        if link != "None":
            valid_url_found = False
            driver.get(link)

            try:
                while not valid_url_found:
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "spotlight")))
                    element = driver.find_element_by_class_name("spotlight")
                    img_url = element.get_attribute('src')

                    if img_url.find('.gif') == -1:
                        valid_url_found = True
                        urls.append(img_url)
            except:
                urls.append("None")
        else:
            urls.append("None")

    return urls


# -------------------------------------------------------------
# -------------------------------------------------------------

# takes a url and downloads image from that url
def image_downloader(img_links, folder_name):
    img_names = []

    try:
        parent = os.getcwd()
        try:
            folder = os.path.join(os.getcwd(), folder_name)
            create_folder(folder)
            os.chdir(folder)
        except:
            print("Error in changing directory.")

        for link in img_links:
            img_name = "None"

            if link != "None":
                img_name = (link.split('.jpg')[0]).split('/')[-1] + '.jpg'

                # this is the image id when there's no profile pic
                if img_name == "10354686_10150004552801856_220367501106153455_n.jpg":
                    img_name = "None"
                else:
                    try:
                        urllib.request.urlretrieve(link, img_name)
                    except:
                        img_name = "None"

            img_names.append(img_name)

        os.chdir(parent)
    except:
        print("Exception (image_downloader):", sys.exc_info()[0])

    return img_names


# -------------------------------------------------------------
# -------------------------------------------------------------

def check_height(driver):
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height


# -------------------------------------------------------------
# -------------------------------------------------------------

# helper function: used to scroll the page
def scroll(driver):
    global old_height
    current_scrolls = 0

    while (True):
        try:
            if current_scrolls == total_scrolls:
                return

            old_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            WebDriverWait(driver, scroll_time, 0.5).until(lambda driver: check_height(driver))
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
        status = x.find_element_by_xpath(".//div[@class='_5wj-']").text
    except:
        try:
            status = x.find_element_by_xpath(".//div[@class='userContent']").text
        except:
            pass
    return status


def get_div_links(x, tag):
    try:
        temp = x.find_element_by_xpath(".//div[@class='_3x-2']")
        return temp.find_element_by_tag_name(tag)
    except:
        return ""


def get_title_links(title):
    l = title.find_elements_by_tag_name('a')
    return l[-1].text, l[-1].get_attribute('href')


def get_title(x):
    title = ""
    try:
        title = x.find_element_by_xpath(".//span[@class='fwb fcg']")
    except:
        try:
            title = x.find_element_by_xpath(".//span[@class='fcg']")
        except:
            try:
                title = x.find_element_by_xpath(".//span[@class='fwn fcg']")
            except:
                pass
    finally:
        return title


def get_time(x):
    time = ""
    try:
        time = x.find_element_by_tag_name('abbr').get_attribute('title')
        time = str("%02d" % int(time.split(", ")[1].split()[1]), ) + "-" + str(
            ("%02d" % (int((list(calendar.month_abbr).index(time.split(", ")[1].split()[0][:3]))),))) + "-" + \
               time.split()[3] + " " + str("%02d" % int(time.split()[5].split(":")[0])) + ":" + str(
            time.split()[5].split(":")[1])
    except:
        pass

    finally:
        return time


def extract_and_write_posts(elements, filename):
    try:
        f = open(filename, "w", newline='\r\n')
        f.writelines(' TIME || TYPE  || TITLE || STATUS  ||   LINKS(Shared Posts/Shared Links etc) ' + '\n' + '\n')

        for x in elements:
            try:
                video_link = " "
                title = " "
                status = " "
                link = ""
                img = " "
                time = " "

                # time
                time = get_time(x)

                # title
                title = get_title(x)
                if title.text.find("shared a memory") != -1:
                    x = x.find_element_by_xpath(".//div[@class='_1dwg _1w_m']")
                    title = get_title(x)

                status = get_status(x)
                if title.text == driver.find_element_by_id("fb-timeline-cover-name").text:
                    if status == '':
                        temp = get_div_links(x, "img")
                        if temp == '':  # no image tag which means . it is not a life event
                            link = get_div_links(x, "a").get_attribute('href')
                            type = "status update without text"
                        else:
                            type = 'life event'
                            link = get_div_links(x, "a").get_attribute('href')
                            status = get_div_links(x, "a").text
                    else:
                        type = "status update"
                        if get_div_links(x, "a") != '':
                            link = get_div_links(x, "a").get_attribute('href')

                elif title.text.find(" shared ") != -1:

                    x1, link = get_title_links(title)
                    type = "shared " + x1

                elif title.text.find(" at ") != -1 or title.text.find(" in ") != -1:
                    if title.text.find(" at ") != -1:
                        x1, link = get_title_links(title)
                        type = "check in"
                    elif title.text.find(" in ") != 1:
                        status = get_div_links(x, "a").text

                elif title.text.find(" added ") != -1 and title.text.find("photo") != -1:
                    type = "added photo"
                    link = get_div_links(x, "a").get_attribute('href')

                elif title.text.find(" added ") != -1 and title.text.find("video") != -1:
                    type = "added video"
                    link = get_div_links(x, "a").get_attribute('href')

                else:
                    type = "others"

                if not isinstance(title, str):
                    title = title.text

                status = status.replace("\n", " ")
                title = title.replace("\n", " ")

                line = str(time) + " || " + str(type) + ' || ' + str(title) + ' || ' + str(status) + ' || ' + str(
                    link) + "\n"

                try:
                    f.writelines(line)
                except:
                    print('Posts: Could not map encoded characters')
            except:
                pass
        f.close()
    except:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info()[0])

    return


# -------------------------------------------------------------
# -------------------------------------------------------------


def save_to_file(driver, name, elements, status, current_section):
    """helper function used to save links to files"""

    # status 0 = dealing with friends list
    # status 1 = dealing with photos
    # status 2 = dealing with videos
    # status 3 = dealing with about section
    # status 4 = dealing with posts

    try:
        f = None  # file pointer

        if status != 4:
            f = open(name, 'w', encoding='utf-8', newline='\r\n')

        results = []
        img_names = []

        # dealing with Friends
        if status == 0:
            # get profile links of friends
            results = [x.get_attribute('href') for x in elements]
            results = [create_original_link(x) for x in results]

            # get names of friends
            people_names = [x.find_element_by_tag_name("img").get_attribute("aria-label") for x in elements]

            # download friends' photos
            try:
                if download_friends_photos:
                    if friends_small_size:
                        img_links = [x.find_element_by_css_selector('img').get_attribute('src') for x in elements]
                    else:
                        links = []
                        for friend in results:
                            try:
                                driver.get(friend)
                                WebDriverWait(driver, 30).until(
                                    EC.presence_of_element_located((By.CLASS_NAME, "profilePicThumb")))
                                l = driver.find_element_by_class_name("profilePicThumb").get_attribute('href')
                            except:
                                l = "None"

                            links.append(l)

                        for i in range(len(links)):
                            if links[i] is None:
                                links[i] = "None"
                            elif links[i].find('picture/view') != -1:
                                links[i] = "None"

                        img_links = get_facebook_images_url(links)

                    folder_names = ["Friend's Photos", "Mutual Friends' Photos", "Following's Photos",
                                    "Follower's Photos", "Work Friends Photos",
                                    "College Friends Photos", "Current City Friends Photos", "Hometown Friends Photos"]
                    print("Downloading " + folder_names[current_section])

                    img_names = image_downloader(img_links, folder_names[current_section])
                else:
                    img_names = ["None"] * len(results)
            except:
                print("Exception (Images)", str(status), "Status =", current_section, sys.exc_info()[0])

        # dealing with Photos
        elif status == 1:
            results = [x.get_attribute('href') for x in elements]
            results.pop(0)

            try:
                if download_uploaded_photos:
                    if photos_small_size:
                        background_img_links = driver.find_elements_by_xpath("//*[contains(@id, 'pic_')]/div/i")
                        background_img_links = [x.get_attribute('style') for x in background_img_links]
                        background_img_links = [((x.split('(')[1]).split(')')[0]).strip('"') for x in
                                                background_img_links]
                    else:
                        background_img_links = get_facebook_images_url(results)

                    folder_names = ["Uploaded Photos", "Tagged Photos"]
                    print("Downloading " + folder_names[current_section])

                    img_names = image_downloader(background_img_links, folder_names[current_section])
                else:
                    img_names = ["None"] * len(results)
            except:
                print("Exception (Images)", str(status), "Status =", current_section, sys.exc_info()[0])

        # dealing with Videos
        elif status == 2:
            results = elements[0].find_elements_by_css_selector('li')
            results = [x.find_element_by_css_selector('a').get_attribute('href') for x in results]

            try:
                if results[0][0] == '/':
                    results = [r.pop(0) for r in results]
                    results = [("https://en-gb.facebook.com/" + x) for x in results]
            except:
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
            for i in range(len(results)):
                # friend's profile link
                f.writelines(results[i])
                f.write(',')

                # friend's name
                f.writelines(people_names[i])
                f.write(',')

                # friend's downloaded picture id
                f.writelines(img_names[i])
                f.write('\n')

        elif status == 1:
            for i in range(len(results)):
                # image's link
                f.writelines(results[i])
                f.write(',')

                # downloaded picture id
                f.writelines(img_names[i])
                f.write('\n')

        elif status == 2:
            for x in results:
                f.writelines(x + "\n")

        f.close()

    except:
        print("Exception (save_to_file)", "Status =", str(status), sys.exc_info()[0])

    return


# ----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def scrape_data(driver, id, scan_list, section, elements_path, save_status, file_names):
    """Given some parameters, this function can scrap friends/photos/videos/about/posts(statuses) of a profile"""
    page = []

    if save_status == 4:
        page.append(id)

    for i in range(len(section)):
        page.append(id + section[i])

    for i in range(len(scan_list)):
        driver.get(page[i])

        if (save_status == 0) or (save_status == 1) or (
                save_status == 2):  # Only run this for friends, photos and videos

            # the bar which contains all the sections
            try:
                sections_bar = driver.find_element_by_xpath("//*[@class='_3cz'][1]/div[2]/div[1]")
                if sections_bar.text.find(scan_list[i]) == -1:
                    continue
            except NoSuchElementException:
                pass

        if save_status != 3:
            scroll(driver)

        data = driver.find_elements_by_xpath(elements_path[i])

        save_to_file(driver, file_names[i], data, save_status, i)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def create_original_link(url):
    if url.find(".php") != -1:
        original_link = facebook_https_prefix + ".facebook.com/" + ((url.split("="))[1])

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = facebook_https_prefix + ".facebook.com/" + ((url.split("/"))[-1].split("?")[0])
    elif url.find("_tab") != -1:
        original_link = facebook_https_prefix + ".facebook.com/" + (url.split("?")[0]).split("/")[-1]
    else:
        original_link = url

    return original_link


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
def create_folder(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)


def scrap_profile(driver, ids):
    folder = os.path.join(os.getcwd(), "Data")
    create_folder(folder)
    os.chdir(folder)

    # execute for all profiles given in input.txt file
    for id in ids:

        driver.get(id)
        url = driver.current_url
        id = create_original_link(url)

        print("\nScraping:", id)

        try:
            target_dir = os.path.join(folder, id.split('/')[-1])
            create_folder(target_dir)
            os.chdir(target_dir)
        except:
            print("Some error occurred in creating the profile directory.")
            continue

        # ----------------------------------------------------------------------------
        print("----------------------------------------")
        print("Friends..")
        # setting parameters for scrape_data() to scrape friends
        scan_list = ["All", "Mutual Friends", "Following", "Followers", "Work", "College", "Current City", "Hometown"]
        section = ["/friends", "/friends_mutual", "/following", "/followers", "/friends_work", "/friends_college",
                   "/friends_current_city",
                   "/friends_hometown"]
        elements_path = ["//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                         "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                         "//*[contains(@class,'_3i9')][1]/div/div/ul/li[1]/div[2]/div/div/div/div/div[2]/ul/li/div/a",
                         "//*[contains(@class,'fbProfileBrowserListItem')]/div/a",
                         "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                         "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                         "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a",
                         "//*[contains(@id,'pagelet_timeline_medley_friends')][1]/div[2]/div/ul/li/div/a"]
        file_names = ["All Friends.txt", "Mutual Friends.txt", "Following.txt", "Followers.txt", "Work Friends.txt",
                      "College Friends.txt",
                      "Current City Friends.txt", "Hometown Friends.txt"]
        save_status = 0

        scrape_data(driver, id, scan_list, section, elements_path, save_status, file_names)
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

        scrape_data(driver, id, scan_list, section, elements_path, save_status, file_names)
        print("Photos Done!")

        # ----------------------------------------------------------------------------
        print("----------------------------------------")
        print("Videos:")
        # setting parameters for scrape_data() to scrap videos
        scan_list = ["'s Videos", "Videos of"]
        section = ["/videos_by", "/videos_of"]
        elements_path = ["//*[contains(@id, 'pagelet_timeline_app_collection_')]/ul"] * 2
        file_names = ["Uploaded Videos.txt", "Tagged Videos.txt"]
        save_status = 2

        scrape_data(driver, id, scan_list, section, elements_path, save_status, file_names)
        print("Videos Done!")
        # ----------------------------------------------------------------------------

        print("----------------------------------------")
        print("About:")
        # setting parameters for scrape_data() to scrap the about section
        scan_list = [None] * 7
        section = ["/about?section=overview", "/about?section=education", "/about?section=living",
                   "/about?section=contact-info", "/about?section=relationship", "/about?section=bio",
                   "/about?section=year-overviews"]
        elements_path = ["//*[contains(@id, 'pagelet_timeline_app_collection_')]/ul/li/div/div[2]/div/div"] * 7
        file_names = ["Overview.txt", "Work and Education.txt", "Places Lived.txt", "Contact and Basic Info.txt",
                      "Family and Relationships.txt", "Details About.txt", "Life Events.txt"]
        save_status = 3

        scrape_data(driver, id, scan_list, section, elements_path, save_status, file_names)
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

        scrape_data(driver, id, scan_list, section, elements_path, save_status, file_names)
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


def login():
    """ Logging into our own profile """

    global driver

    ffprofile = webdriver.FirefoxProfile("/home/zeryx/.mozilla/firefox/qs23tl6v.default")
    gecko_path = os.path.join(os.getcwd(), "bin", "geckodriver")
    # options.add_argument("headless")

    driver = webdriver.Firefox(firefox_profile=ffprofile, executable_path=gecko_path)

    fb_path = facebook_https_prefix + "facebook.com"
    driver.get(fb_path)
    driver.maximize_window()
    WebDriverWait(driver, timeout=5)

    # filling the form
    # driver.find_element_by_name('email').send_keys(email)
    # driver.find_element_by_name('pass').send_keys(password)

    # clicking on login button
    # driver.find_element_by_id('loginbutton').click()

    # if your account uses multi factor authentication
    # mfa_code_input = safe_find_element_by_id(driver, 'approvals_code')
    #
    # if mfa_code_input is None:
    #     return
    #
    # mfa_code_input.send_keys(input("Enter MFA code: "))
    # driver.find_element_by_id('checkpointSubmitButton').click()

    # there are so many screens asking you to verify things. Just skip them all
    while safe_find_element_by_id(driver, 'checkpointSubmitButton') is not None:
        dont_save_browser_radio = safe_find_element_by_id(driver, 'u_0_3')
        if dont_save_browser_radio is not None:
            dont_save_browser_radio.click()

        driver.find_element_by_id('checkpointSubmitButton').click()
    return driver


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

def execute(input):
    cred_path = os.path.join(os.getcwd(), "creds", "credentials.txt")
    with open(cred_path) as f:
        email = f.readline().split('"')[1]
        password = f.readline().split('"')[1]

        if email == "" or password == "":
            print("Your email or password is missing. Kindly write them in credentials.txt")
            exit()

    ids = [facebook_https_prefix + "facebook.com/" + line.split("/")[-1] for line in input]

    print("\nStarting Scraping...")

    driver = login()
    scrap_profile(driver, ids)
    driver.close()


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------