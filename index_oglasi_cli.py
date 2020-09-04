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

XPATH_CAR_REGISTRATION = "/html/body/div[5]/div/div/div[1]/ul/li[1]/div[2]/div[@class=\"features_list oglasHolder_1\"]"
XPATH_CAR_DESCRIPTION = "/html/body/div[5]/div/div/div[1]/ul/li[1]/div[2]/div[@class=\"oglas_description\"]"


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
        self.ad_title = adHolder.find_element_by_xpath(XPATH_AD_TITLE).text
        self.ad_location = adHolder.find_element_by_xpath(XPATH_AD_LOCATION).text
        self.ad_price = adHolder.find_element_by_xpath(XPATH_AD_PRICE).text
        self.ad_link = adHolder.find_element_by_xpath(XPATH_AD_LINK).get_attribute("href")
        self.price_num = float(self.ad_price.replace("€", "").replace(".", "").replace(",", "."))
        self.ad_oglas_description = ""

    def __repr__(self):
        return ("%s %s %s %s" % ('{:.^10s}'.format(self.ad_price), '{:.^40.40s}'.format(self.ad_title), '{:.^10.10s}'.format(self.ad_location), self.ad_link))

    def addDetails(self, adHolder):
        self.ad_oglas_description = adHolder.find_element_by_xpath(XPATH_CAR_DESCRIPTION).text

class CarAd(GenericAd):
    def __init__(self, adHolder):
        super.__init__(adHolder)
        self.registriran_do = ""

    def __repr__(self):
        # return ("%s %s %s %s %s" % ('{:.^10s}'.format(self.ad_price), '{:.^7s}'.format(self.registriran_do), '{:.^40.40s}'.format(self.ad_title), '{:.^10.10s}'.format(self.ad_location), self.ad_link))
        return ("%s %s %s %s %s" % ('{:.^10s}'.format(self.ad_price), '{:.^7s}'.format(self.registriran_do), '{:.^40.40s}'.format(self.ad_title), '{:.^10.10s}'.format(self.ad_location), self.ad_link))

    def addDetails(self, adHolder):
        super().addDetails(adHolder)
        self.ad_registriran_do = adHolder.find_element_by_xpath(XPATH_CAR_REGISTRATION).text
        registriran_do = self.ad_registriran_do.split('\n')
        self.registriran_do = ""
        for s in registriran_do:
            if ("Registriran do" in s):
                self.registriran_do = s.split(" ")[2]

class HouseAd(GenericAd):
    pass

def save_cars(cars, filename):
    pickle.dump(cars, open(filename, "wb"))


def load_cars(filename):
    return pickle.load(open(filename, "rb"))


def getCarsFromSite(driver, totalCars):
    cars = []
    adHolders = driver.find_elements_by_xpath(XPATH_AD_HOLDER)
    for ad in adHolders:
        cars.append(CarAd(ad))
        print("ADD:", str(len(cars)) + "/" + str(totalCars))
    return cars


def addDetailsToCars(driver, cars, totalCars):
    for e, car in enumerate(cars):
        print("ADD DETAIL:", str(e) + "/" + str(totalCars))
        if (car.ad_oglas_description == ""):
            driver.get(car.ad_link)
            car.addDetails(driver)

def getCars(driver, cars):
    # init
    driver.get(getSite(SEARCH_SITE_CAR, elementsNum=100, priceFrom=530, priceTo=540))

    totalCars = getAdNum(driver)

    cars.extend(getCarsFromSite(driver, totalCars))
    while(goToNextSite(driver)):
        cars.extend(getCarsFromSite(driver, totalCars))

    addDetailsToCars(driver, cars, totalCars)

    cars.sort(key=operator.attrgetter('price_num'))

def words_in_string(word_list, a_string):
    return set(word_list).intersection(a_string.split())

if __name__ == "__main__":
    # driver = getDriver()
    cars = []
    # getCars(driver, cars)
    # cars.extend(load_cars("cars_100_200.p"))
    # cars.extend(load_cars("cars_201_300.p"))
    # cars.extend(load_cars("cars_301_400.p"))
    # cars.extend(load_cars("cars_401_500.p"))
    # cars.extend(load_cars("cars_501_600.p"))
    # cars.extend(load_cars("cars_601_700.p"))
    cars.extend(load_cars("cars_100_700.p"))
    # save_cars(cars,"houses_50001_60000.p" )

    # clean_cars = []

    # ignore_words = ["disel", "diesel", "audi", "bmw", "mercedes"]
    # for car in cars:
    #     if "2021" in car.registriran_do:
    #         if not words_in_string(ignore_words, car.ad_title.lower()):
    #             if not words_in_string(ignore_words, car.ad_oglas_description.lower()):
    #                 clean_cars.append(car)
    
    # driver = getDriver()
    # for car in clean_cars:
    #     driver.get(car.ad_link)
    #     car.extra_info = driver.find_element_by_xpath("/html/body/div[5]").text

    # new_clean_cars = []

    # for car in clean_cars:
    #     if not words_in_string(ignore_words, car.extra_info.lower()):
    #         new_clean_cars.append(car)