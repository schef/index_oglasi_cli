#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

SEARCH_SITE = "https://www.index.hr/oglasi/osobni-automobili/gid/27"
XPATH_AD_NUM = "/html/body/div[4]/div/div/div[1]/strong"
XPATH_NEXT_SITE_BUTTON = "/html/body/div[5]/div/div/div[3]/div[4]/ul/li[8]/a"
XPATH_CURRENT_SITE_NUM = "/html/body/div[5]/div/div/div[3]/div[4]/ul/li[@class=\"active\"]/a"

def getAdNum(driver):
    return int(driver.find_element_by_xpath(XPATH_AD_NUM).text.replace(".", ""))

def getCurrentSiteNum(driver):
    return int(driver.find_element_by_xpath(XPATH_CURRENT_SITE_NUM).text)

def goToNextSite(driver):
    nextSiteButton = driver.find_element_by_xpath(XPATH_NEXT_SITE_BUTTON)
    nextSiteButton.click()

if __name__ == "__main__":
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox()
    driver.get(SEARCH_SITE)