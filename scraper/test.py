#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Options
options = Options()

## Option for using a custom Firefox profile
#options.profile = '/home/t00m/.basico/opt/webdrivers/basico.default'

## Enable headless
options.headless = False

# Specify custom geckodriver path
service = Service('bin/chromedriver')

# Test
browser = webdriver.Chrome(options=options, service=service)
browser.get('https://dev.to')
print(browser.title)
browser.quit()
