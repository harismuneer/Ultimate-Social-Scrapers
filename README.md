# 🔥 Ultimate Facebook Scrapper 

[![DOI](https://zenodo.org/badge/145763277.svg)](https://zenodo.org/badge/latestdoi/145763277)

[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg?style=for-the-badge&logo=appveyor)](#)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](#)
[![GitHub Forks](https://img.shields.io/github/forks/harismuneer/Ultimate-Facebook-Scraper.svg?style=social&label=Fork&maxAge=2592000)](https://www.github.com/harismuneer/Ultimate-Facebook-Scraper/fork)
[![GitHub Issues](https://img.shields.io/github/issues/harismuneer/Ultimate-Facebook-Scraper.svg?style=flat&label=Issues&maxAge=2592000)](https://www.github.com/harismuneer/Ultimate-Facebook-Scraper/issues)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat&label=Contributions&colorA=red&colorB=black	)](#)


A bot which scrapes almost everything about a facebook user's profile including

* uploaded photos
* tagged photos
* videos
* friends list and their profile photos (including Followers, Following, Work Friends, College Friends etc)
* and all public posts/statuses available on the user's timeline.

The best thing about this scraper is that the data is scraped in an organized format so that it can be used for educational/research purpose by researchers. Moreover, this scraper does not use Facebook's Graph API so there are no rate limiting issues as such. 

**This tool is being used by thousands of developers weekly and we are pretty amazed at this response! Thankyou guys!🎉**

For details regarding **citing/referencing** this tool for your research, check the 'Citation' section below.

## Note
At its core, this tool uses xpaths of **'divs'** to extract data from them. Since Facebook keeps on updating its site frequently and the 'divs' get changed. Consequently, we have to update the divs accordingly to correctly scrape the data. 

The developers of this tool have devoted a lot of time and effort in developing and most importantly maintaining this tool for quite a lot time now. **In order to keep this amazing tool alive, we need support from you geeks.**

The code is pretty intuitive and easy to understand, so you can update the relevant xpaths in the code when you feel that you have tried many profiles and the data isn't being scraped for any of them (that's a hint that Facebook has updated their site) and generate a pull request. That's quite an easy thing to do. Thanks!

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

Run the code using Python 3. Also, the code is multi-platform and is tested on both Windows and Linux.
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

## Citation

[![DOI](https://zenodo.org/badge/145763277.svg)](https://zenodo.org/badge/latestdoi/145763277)

If you use this tool for your research, then kindly cite it. Click the above badge for more information regarding the complete citation for this tool and diffferent citation formats like IEEE, APA etc.




----------------------------------------------------------------------------------------------------------------------------------------

## Important Message
This tool is for research purposes only. Hence, the developers of this tool won't be responsible for any misuse of data collected using this tool. 

----------------------------------------------------------------------------------------------------------------------------------------

## Authors
You can get in touch with us on our LinkedIn Profiles:

#### Haris Muneer
[![LinkedIn Link](https://img.shields.io/badge/Connect-harismuneer-blue.svg?logo=linkedin&longCache=true&style=social&label=Connect
)](https://www.linkedin.com/in/harismuneer)

You can also follow my GitHub Profile to stay updated about my latest projects: [![GitHub Follow](https://img.shields.io/badge/Connect-harismuneer-blue.svg?logo=Github&longCache=true&style=social&label=Follow)](https://github.com/harismuneer)

#### Hassaan Elahi
[![LinkedIn Link](https://img.shields.io/badge/Connect-Hassaan--Elahi-blue.svg?logo=linkedin&longCache=true&style=social&label=Connect)](https://www.linkedin.com/in/hassaan-elahi/)

You can also follow my GitHub Profile to stay updated about my latest projects:[![GitHub Follow](https://img.shields.io/badge/Connect-Hassaan--Elahi-blue.svg?logo=Github&longCache=true&style=social&label=Follow)](https://github.com/Hassaan-Elahi)


If you liked the repo then kindly support it by giving it a star ⭐!

## Contributions Welcome
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](#)

If you find any bug in the code or have any improvements in mind then feel free to generate a pull request.

## Issues
[![GitHub Issues](https://img.shields.io/github/issues/harismuneer/Ultimate-Facebook-Scraper.svg?style=flat&label=Issues&maxAge=2592000)](https://www.github.com/harismuneer/Ultimate-Facebook-Scraper/issues)

If you face any issue, you can create a new issue in the Issues Tab and I will be glad to help you out.

## License
[![MIT](https://img.shields.io/cocoapods/l/AFNetworking.svg?style=style&label=License&maxAge=2592000)](../master/LICENSE)

Copyright (c) 2018-present, harismuneer, Hassaan-Elahi                                                        
