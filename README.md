# Ultimate Facebook Scrapper
A bot which scrapes almost everything about a facebook user's profile including

* uploaded photos
* tagged photos
* videos
* friends list and their profile photos (including Followers, Following, Work Friends, College Friends etc)
* and all public posts/statuses available on the user's timeline.

The best thing about this scraper is that the data is scraped in an organized format so that it can be used for educational/research purpose by researchers.

## Sample
<p align="middle">
  <img src="../master/images/main.png" width="700"/>
 </p>


## Screenshot
<p align="middle">
  <img src="../master/images/screenshot.png" width="700"/>
 </p>


----------------------------------------------------------------------------------------------------------------------------------------
## Usage

### Installation
You will need to install latest version of [Google Chrome](https://www.google.com/chrome/). Moreover, you need to install selenium module as well using

```
pip install selenium
```

Run the code using Python 3.
The tool uses latest version of [Chrome Web Driver](http://chromedriver.chromium.org/downloads). I have placed the webdriver along with the code but if that version doesn't work then replace the chrome web driver with the latest one.

### How to Run
There's a file named "input.txt". You can add as many profiles as you want in the following format with each link on a new line:

```
https://www.facebook.com/andrew.ng.96
https://www.facebook.com/zuck
```

Make sure the link only contains the username or id number at the end and not any other stuff. Make sure its in the format mentioned above.

Note: There are two modes to download Friends Profile Pics and the user's Photos: Large Size and Small Size. You can change the following variables. By default they are set to Small Sized Pics because its really quick while Large Size Mode takes time depending on the number of pictures to download

```
# whether to download the full image or its thumbnail (small size)
# if small size is True then it will be very quick else if its False then it will open each photo to download it
# and it will take much more time
friends_small_size = True
photos_small_size = True
```

----------------------------------------------------------------------------------------------------------------------------------------

## Note
This tool is for research purposes only. Hence, the developers of this tool won't be responsible for any misuse of data collected using this tool. 

----------------------------------------------------------------------------------------------------------------------------------------

## Contact
You can get in touch with me on my LinkedIn Profile: [Haris Muneer](https://www.linkedin.com/in/harismuneer/)

## Issues
If you face any issue, you can create a new issue in the Issues Tab and I will be glad to help you out.

## License
[MIT](../master/LICENSE)
Copyright (c) 2018-present, harismuneer, Hassaan-Elahi


