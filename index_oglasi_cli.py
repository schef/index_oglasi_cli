#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import operator
import pickle

SEARCH_SITE_CAR = "https://www.index.hr/oglasi/osobni-automobili/gid/27"
SEARCH_SITE_HOUSE = "https://www.index.hr/oglasi/prodaja-kuca/gid/3276"
SEARCH_ADD_ELEMENTS_NUM = "elementsNum"
SEARCH_ADD_PRICE_FROM = "cijenaod"
SEARCH_ADD_PRICE_TO = "cijenado"
SEARCH_ADD_LOCATION = "pojamZup"
SEARCH_ADD_LOCATION_MEDIMURSKA = "1159"
SEARCH_ADD_LOCATION_VARAZDINSKA = "1166"

XPATH_AD_NUM = "/html/body/div[4]/div/div/div[1]/strong"
XPATH_NEXT_SITE_BUTTON = "/html/body/div[5]/div/div/div[3]/div[4]/ul/li[8]/a"
XPATH_CURRENT_SITE_NUM = "/html/body/div[5]/div/div/div[3]/div[4]/ul/li[@class=\"active\"]/a"
XPATH_AD_HOLDER = "/html/body/div[5]/div/div/div[3]/div[2]/div[@class=\"OglasiRezHolder\"]"
XPATH_AD_TITLE = "./a/span/span[1]/span[1]"
XPATH_AD_LOCATION = "./a/span/span[2]/ul/li[1]"
XPATH_AD_PRICE = "./a/span/span[2]/span/span"
XPATH_AD_LINK = "./a"

XPATH_AD_DETAILS_ID = "PrintOglasContent"
XPATH_AD_DETAILS_DESCRIPTION = "/html/body/div[5]/div/div/div[1]/ul/li[1]/div[2]/div[@class=\"oglas_description\"]"
XPATH_AD_DETAILS_TABLES = "features_list"

def getDriver():
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox()
    return driver


def getSite(site, elementsNum=10, priceFrom=None, priceTo=None, location=None):
    if elementsNum or priceFrom or priceTo or location:
        site += "?"
        if (elementsNum):
            site += str(SEARCH_ADD_ELEMENTS_NUM) + "=" + str(elementsNum) + "&"
        if (priceFrom):
            site += str(SEARCH_ADD_PRICE_FROM) + "=" + str(priceFrom) + "&"
        if (priceTo):
            site += str(SEARCH_ADD_PRICE_TO) + "=" + str(priceTo) + "&"
        if (location):
            site += str(SEARCH_ADD_LOCATION) + "=" + str(location) + "&"
        site = site[:-1]
    return site


def getAdNum(driver):
    return int(driver.find_element_by_xpath(XPATH_AD_NUM).text.replace(".", ""))


def getCurrentSiteNum(driver):
    return int(driver.find_element_by_xpath(XPATH_CURRENT_SITE_NUM).text)


def goToNextSite(driver):
    try:
        nextSite = driver.find_element_by_xpath(XPATH_NEXT_SITE_BUTTON).get_attribute("href")
        driver.get(nextSite)
        return True
    except:
        return False


class GenericAd():
    def __init__(self, adHolder):
        try:
            self.ad_title = adHolder.find_element_by_xpath(XPATH_AD_TITLE).text
        except:
            self.ad_title = ""
        try:
            self.ad_location = adHolder.find_element_by_xpath(XPATH_AD_LOCATION).text
        except:
            self.ad_location = ""
        try:
            self.ad_price = adHolder.find_element_by_xpath(XPATH_AD_PRICE).text
        except:
            self.ad_price = "0"
        self.price_num = float(self.ad_price.replace("€", "").replace(".", "").replace(",", "."))
        self.ad_link = adHolder.find_element_by_xpath(XPATH_AD_LINK).get_attribute("href")
        self.ad_details_all = ""
        self.ad_details_description = ""
        self.ad_details_tables = []

    def __repr__(self):
        return ("%s %s %s %s" % ('{:.^10s}'.format(self.ad_price), '{:.^40.40s}'.format(self.ad_title), '{:.^10.10s}'.format(self.ad_location), self.ad_link))

    def addDetails(self, adHolder):
        try:
            self.ad_details_all = adHolder.find_element_by_id(XPATH_AD_DETAILS_ID).text
        except:
            self.ad_details_all = ""
        try:
            self.ad_details_tables = [x.text for x in adHolder.find_elements_by_class_name(XPATH_AD_DETAILS_TABLES)]
        except:
            self.ad_details_tables = []
        try:
            self.ad_details_description = adHolder.find_element_by_xpath(XPATH_AD_DETAILS_DESCRIPTION).text
        except:
            self.ad_details_description = ""

class CarAd(GenericAd):
    def __init__(self, adHolder):
        GenericAd.__init__(self, adHolder)
        self.registriran_do = ""

    def __repr__(self):
        return ("%s %s %s %s %s" % ('{:.^10s}'.format(self.ad_price), '{:.^7s}'.format(self.registriran_do), '{:.^40.40s}'.format(self.ad_title), '{:.^10.10s}'.format(self.ad_location), self.ad_link))

    def addDetails(self, adHolder):
        GenericAd.addDetails(self, adHolder)
        self.registriran_do = ""
        for table in self.ad_details_tables:
            for word in table.split("\n"):
                if ("Registriran do" in word):
                    self.registriran_do = word.split(" ")[2]


class HouseAd(GenericAd):
    def __init__(self, adHolder):
        GenericAd.__init__(self, adHolder)
        self.zamjena = ""

    def __repr__(self):
        return ("%s %s %s %s %s" % ('{:.^10s}'.format(self.ad_price), '{:.^2s}'.format(self.zamjena), '{:.^40.40s}'.format(self.ad_title), '{:.^10.10s}'.format(self.ad_location), self.ad_link))

    def addDetails(self, adHolder):
        GenericAd.addDetails(self, adHolder)
        self.zamjena = ""
        for table in self.ad_details_tables:
            for word in table.split("\n"):
                if ("Zamjena" in word):
                    self.zamjena = word.split(" ")[1]

def saveAds(ads, filename):
    pickle.dump(ads, open(filename, "wb"))


def loadAds(filename):
    return pickle.load(open(filename, "rb"))


def getAdFromSite(driver, ads, classAd, totalAds):
    adHolders = driver.find_elements_by_xpath(XPATH_AD_HOLDER)
    for ad in adHolders:
        ads.append(classAd(ad))
        print("ADD:", str(len(ads)) + "/" + str(totalAds))


def addDetailsToAd(driver, ads, totalAds):
    for e, ad in enumerate(ads):
        print("ADD DETAIL:", str(e) + "/" + str(totalAds))
        if (ad.ad_details_description == ""):
            driver.get(ad.ad_link)
            ad.addDetails(driver)
            if e % 100 == 0:
                driver.close()
                driver = getDriver()


def getAds(driver, ads, site, classAd, elementsNum=10, priceFrom="", priceTo=""):
    driver.get(getSite(site, elementsNum=100, priceFrom=priceFrom, priceTo=priceTo))
    totalAds = getAdNum(driver)
    getAdFromSite(driver, ads, classAd, totalAds)
    while(goToNextSite(driver)):
        getAdFromSite(driver, ads, classAd, totalAds)
    addDetailsToAd(driver, ads, totalAds)
    ads.sort(key=operator.attrgetter('price_num'))


def wordsInString(word_list, a_string):
    return set(word_list).intersection(a_string.split())


if __name__ == "__main__":
    driver = getDriver()
    # cars = []
    # getAds(driver, cars, SEARCH_SITE_CAR, CarAd, 10, 510, 520)

    houses = []
    # getAds(driver, houses, SEARCH_SITE_HOUSE, HouseAd, 100, 0, 75000)
    # saveAds(houses, "houses_0_75000.p")
    houses = loadAds("houses_0_75000.p")
    addDetailsToAd(driver, houses, 0)