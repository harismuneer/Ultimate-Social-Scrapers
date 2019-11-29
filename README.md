<a href="#">
  <div align="center">
    <img src="images/ufs_icon.png" width='154'/>
  </div>
</a>

<h1 align="center">Ultimate Facebook Scraper (UFS)</h1>

<p align="center">
  Tooling that <b>automates</b> your social media interactions to collect posts, photos, videos, friends, followers and much more on Facebook.
</p>

<p align="center">
  <a href="https://www.codacy.com/manual/harismuneer/Ultimate-Facebook-Scraper?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=harismuneer/Ultimate-Facebook-Scraper&amp;utm_campaign=Badge_Grade">
    <img src="https://api.codacy.com/project/badge/Grade/7f41790c3c3a4fd29293777c676c8617" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Build-Passing-brightgreen.svg?style=flat-square&logo=appveyor" />
  </a>
  <a href="#">
    <img src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" />
  </a>
  <a href="https://www.github.com/harismuneer/Ultimate-Facebook-Scraper/fork">
    <img src="https://img.shields.io/github/forks/harismuneer/Ultimate-Facebook-Scraper.svg?style=social&label=Fork&maxAge=2592000" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat&label=Contributions&colorA=red&colorB=black" />
  </a>
</p>

<hr>

<h2 align="center">Contributors</h2>
<p align="center">
  Developers from following organizations have so far joined the quest and contributed to UFS.
</p>

<p align="center">
  <a href='#'>
    <img src = "https://www.adbirds.global/wp-content/uploads/2016/07/Microsoft-Logo-square.png" width="150" alt="Microsoft"/>
  </a>
  <img hspace="5"/>
  <a href='#'>
    <img src = "https://autopair.net/images/easyblog_articles/5/MIT-Logo.png" width="165" alt="MIT"/>
  </a>
  <a href='#'>
    <img src = "https://www.globalfinancialdata.com/wp-content/uploads/client-logos/Harvard-University-logo-.jpg" width="163" alt="Harvard"/>
  </a>
  <img hspace="10"/>  
  <a href='#'>
    <img src = "https://upload.wikimedia.org/wikipedia/en/e/e4/National_University_of_Computer_and_Emerging_Sciences_logo.png" width="120" alt="NUCES"/>
  </a><br>      
  <a href='#'>
    <img src = "https://static.wixstatic.com/media/e70787_c0c48d456b0d421b9c0d45478f9f422d~mv2.gif" width="165" alt="UCLA"/>
  </a>
  <img hspace="20" vpsace="5"/>
  <a href='#'>
    <img src = "http://www.geekweek.pk/2016/wp-content/uploads/2016/01/ACM-logo.png" width="280" alt="ACM"/>
  </a>
  <img hspace="20"/>
  <a href='#'>
    <img src = "https://i2.wp.com/www.opfblog.com/wp-content/uploads/2014/10/Lums-Logo.jpg?zoom=1.3499999046325684&fit=500%2C409&ssl=1" width="120" alt="LUMS"/>
  </a>
</p>
  
<hr>

## Features

A bot which scrapes almost everything about a user's Facebook profile including:

- uploaded photos
- tagged photos
- videos
- friends list and their profile photos (including Followers, Following, Work Friends, College Friends etc)
- and all public posts/statuses available on the user's timeline.

Data is scraped in an organized format to be used for educational/research purposes by researchers. This scraper does not use Facebook's Graph API meaning there are no rate limiting issues.

**This tool is being used by thousands of developers weekly and we are pretty amazed at this response! Thank you guys!🎉**

For **citing/referencing** this tool for your research, check the 'Citation' section below.

## Note

This tool uses xpaths of **'divs'** to extract data. Since Facebook updates its site frequently, the 'divs' get changed. Consequently, we have to update the divs accordingly to correctly scrape data.

The developers of this tool have devoted time and effort in developing, and maintaining this tool for a long time. **In order to keep this amazing tool alive, we need support from you geeks.**

The code is intuitive and easy to understand, so you can update the relevant xpaths in the code if you find data is not being scraped from profiles. Facebook has most likely updated their site, so please generate a pull request. Much appreciated!

## Sample

<p align="middle">
  <img src="images/main.png" width="700"/>
 </p>

## Screenshot

<p align="middle">
  <img src="images/screenshot.png" width="700"/>
 </p>

---

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

---

## Citation

<a href="https://zenodo.org/badge/latestdoi/145763277">
  <img src="https://zenodo.org/badge/145763277.svg" />
</a>

If you use this tool for your research, then kindly cite it. Click the above badge for more information regarding the complete citation for this tool and diffferent citation formats like IEEE, APA etc.

---

## Important Message

This tool is for research purposes only. Hence, the developers of this tool won't be responsible for any misuse of data collected using this tool. Used by many researchers and open source intelligence (OSINT) analysts.

This tool will not works if your account was set up with 2FA. You must disable it before using.

---

## Authors

You can get in touch with us on our LinkedIn Profiles:

#### Haris Muneer

[![LinkedIn Link](https://img.shields.io/badge/Connect-harismuneer-blue.svg?logo=linkedin&longCache=true&style=social&label=Connect)](https://www.linkedin.com/in/harismuneer)

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
