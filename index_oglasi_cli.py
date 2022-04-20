#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import operator
import pickle


def getDriver():
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox()
    return driver


class SearchPage:
    SEARCH_SITE_CAR = "https://www.index.hr/oglasi/osobni-automobili/gid/27"
    SEARCH_ADD_ELEMENTS_NUM = "elementsNum"
    SEARCH_ADD_PRICE_FROM = "cijenaod"
    SEARCH_ADD_PRICE_TO = "cijenado"
    SEARCH_ADD_LOCATION = "pojamZup"
    SEARCH_ADD_LOCATION_MEDIMURSKA = "1159"
    SEARCH_ADD_LOCATION_VARAZDINSKA = "1166"

    @staticmethod
    def generateLink(link, elementsNum=10, priceFrom=None, priceTo=None, location=None):
        if elementsNum or priceFrom or priceTo or location:
            link += "?"
            if (elementsNum):
                link += str(SearchPage.SEARCH_ADD_ELEMENTS_NUM) + "=" + str(elementsNum) + "&"
            if (priceFrom):
                link += str(SearchPage.SEARCH_ADD_PRICE_FROM) + "=" + str(priceFrom) + "&"
            if (priceTo):
                link += str(SearchPage.SEARCH_ADD_PRICE_TO) + "=" + str(priceTo) + "&"
            if (location):
                link += str(SearchPage.SEARCH_ADD_LOCATION) + "=" + str(location) + "&"
            link = link[:-1]
        return link

    "/html/body/div[6]/div/div/div[3]/div[4]/ul/li[7]/a"
    XPATH_AD_NUM = "/html/body/div[5]/div/div/div[1]/strong"
    CLASS_NAME_PAGE_BUTTONS = "pagination"
    XPATH_CURRENT_SITE_NUM = "/html/body/div[6]/div/div/div[3]/div[4]/ul/li[@class=\"active\"]/a"
    XPATH_AD_HOLDER = "/html/body/div[6]/div/div/div[3]/div[2]/div[@class=\"OglasiRezHolder\"]"
    XPATH_AD_TITLE = "./a/span/span[1]/span[1]"
    XPATH_AD_LOCATION = "./a/span/span[2]/ul/li[1]"
    XPATH_AD_PRICE = "./a/span/span[2]/span/span"
    XPATH_AD_LINK = "./a"
    ID_CONDITIONS = "didomi-notice-agree-button"

    @staticmethod
    def getCurrentPageNum(driver):
        try:
            return int(driver.find_element(by=By.XPATH, value=SearchPage.XPATH_CURRENT_SITE_NUM).text)
        except:
            print("Cant parse XPATH_CURRENT_SITE_NUM")
            return 0

    @staticmethod
    def goToNextPage(driver):
        try:
            pageButtons = driver.find_element(by=By.CLASS_NAME, value=SearchPage.CLASS_NAME_PAGE_BUTTONS)
            nextSiteList = pageButtons.find_elements(by=By.TAG_NAME, value="a")
            nextSite = nextSiteList[-2].get_attribute("href")
            driver.get(nextSite)
            return True
        except:
            print("Cant go to next site")
            return False

    @staticmethod
    def getTotalAdsNum(driver):
        try:
            return int(driver.find_element(by=By.XPATH, value=SearchPage.XPATH_AD_NUM).text.replace(".", ""))
        except:
            print("Cant parse XPATH_AD_NUM")
            return 0

    @staticmethod
    def getLinkFromAd(ad):
        try:
            return ad.find_element(by=By.XPATH, value=SearchPage.XPATH_AD_LINK).get_attribute("href")
        except:
            print("Cant parse XPATH_AD_LINK")
            return ""

    @staticmethod
    def getAdsFromCurrentPage(driver):
        try:
            return driver.find_elements(by=By.XPATH, value=SearchPage.XPATH_AD_HOLDER)
        except:
            print("Cant parse XPATH_AD_HOLDER")
            return []

    @staticmethod
    def getAdLinksFromCurrentPage(driver):
        ads = SearchPage.getAdsFromCurrentPage(driver)
        links = []
        for ad in ads:
            link = SearchPage.getLinkFromAd(ad)
            if (link):
                links.append(link)
        return links

    @staticmethod
    def acceptConditions(driver):
        button = driver.find_element(by=By.ID, value=SearchPage.ID_CONDITIONS)
        button.click()

class DetailPage:
    XPATH_AD_DETAILS_ID = "PrintOglasContent"
    XPATH_AD_DETAILS_DESCRIPTION = "/html/body/div[6]/div/div/div[1]/ul/li[1]/div[2]/div[@class=\"oglas_description\"]"
    XPATH_AD_DETAILS_TABLES = "features_list"
    XPATH_AD_DETAILS_TITLE = "/html/body/div[6]/div/div/div[1]/div[2]/div[1]"
    XPATH_AD_DETAILS_LOCATION = "/html/body/div[6]/div/div/div[2]/div[1]/ul/li[4]"
    XPATH_AD_DETAILS_PRICE = "/html/body/div[6]/div/div/div[1]/div[2]/div[2]/span"

    @staticmethod
    def getAll(driver):
        try:
            return driver.find_element(by=By.ID, value=DetailPage.XPATH_AD_DETAILS_ID).text
        except:
            print("Cant get XPATH_AD_DETAILS_ID")
            return ""

    @staticmethod
    def getTables(driver):
        try:
            return [x.text for x in driver.find_elements(by=By.CLASS_NAME, value=DetailPage.XPATH_AD_DETAILS_TABLES)]
        except:
            print("Cant get XPATH_AD_DETAILS_TABLES")
            return []

    @staticmethod
    def getDescription(driver):
        try:
            return driver.find_element(by=By.XPATH, value=DetailPage.XPATH_AD_DETAILS_DESCRIPTION).text
        except:
            print("Cant get XPATH_AD_DETAILS_DESCRIPTION")
            return ""

    @staticmethod
    def getRegistriranDo(tables):
        try:
            for table in tables:
                for word in table.split("\n"):
                    if ("Registriran do" in word):
                        return word.split(" ")[2]
            print("Cant find Registriran do")
            return ""
        except:
            print("Cant parse Registriran do")
            return ""

    @staticmethod
    def getTitle(driver):
        try:
            return driver.find_element(by=By.XPATH, value=DetailPage.XPATH_AD_DETAILS_TITLE).text
        except:
            print("Cant get XPATH_AD_DETAILS_TITLE")
            return ""

    @staticmethod
    def getLocation(driver):
        try:
            return driver.find_element(by=By.XPATH, value=DetailPage.XPATH_AD_DETAILS_LOCATION).text
        except:
            print("Cant get XPATH_AD_DETAILS_LOCATION")
            return ""

    @staticmethod
    def getPrice(driver):
        try:
            price = driver.find_element(by=By.XPATH, value=DetailPage.XPATH_AD_DETAILS_PRICE).text
            try:
                return float(price.replace("€", "").replace(".", "").replace(",", "."))
            except:
                print("Cant convert price to float")
                return 0.0
        except:
            print("Cant get XPATH_AD_DETAILS_PRICE")
            return 0.0


class File:
    @staticmethod
    def saveAds(ads, filename):
        pickle.dump(ads, open(filename, "wb"))

    @staticmethod
    def loadAds(filename):
        return pickle.load(open(filename, "rb"))


class CarAd():
    link = ""
    title = ""
    location = ""
    price = 0
    detailsAll = ""
    description = ""
    tables = []
    registriranDo = ""

    def __repr__(self):
        return ("%s %s %s %s %s" % ('{:.^10s}'.format(str(self.price)), '{:.^7s}'.format(self.registriranDo), '{:.^40.40s}'.format(self.title), '{:.^10.10s}'.format(self.location), self.link))


def getCarAdFromLink(driver, link):
    driver.get(link)
    car = CarAd()
    car.link = link
    car.title = DetailPage.getTitle(driver)
    car.location = DetailPage.getLocation(driver)
    car.price = DetailPage.getPrice(driver)
    car.detailsAll = DetailPage.getAll(driver)
    car.description = DetailPage.getDescription(driver)
    car.tables = DetailPage.getTables(driver)
    car.registriranDo = DetailPage.getRegistriranDo(car.tables)
    return car


if __name__ == "__main__":
    driver = getDriver()
    links = []

    # medimurje
    driver.get(SearchPage.generateLink("https://www.index.hr/oglasi/osobni-automobili/gid/27?markavozila=11372&modelvozila=11380"))
    SearchPage.acceptConditions(driver)
    print("Total adds %d" % (SearchPage.getTotalAdsNum(driver)))
    links += SearchPage.getAdLinksFromCurrentPage(driver)
    while (SearchPage.goToNextPage(driver)):
        links += SearchPage.getAdLinksFromCurrentPage(driver)

    # varazdinska
    # driver.get(SearchPage.generateLink(SearchPage.SEARCH_SITE_CAR, elementsNum=100, priceFrom=300, priceTo=1000, location=SearchPage.SEARCH_ADD_LOCATION_VARAZDINSKA))
    # print("Total adds %d" % (SearchPage.getTotalAdsNum(driver)))
    # links += SearchPage.getAdLinksFromCurrentPage(driver)
    # while(SearchPage.goToNextPage(driver)):
    #    links += SearchPage.getAdLinksFromCurrentPage(driver)

    cars = []
    for e, link in enumerate(links):
        print("%d/%d" % (e, len(links)))
        car = getCarAdFromLink(driver, link)
        cars.append(car)
    cars.sort(key=operator.attrgetter('price'))
