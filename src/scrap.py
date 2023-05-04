from abc import ABC, abstractmethod
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0"

class Scrap():
    """ This class instanciates a specific abstract scrapper according to the given URL.

    Attributes:
        scrapper (AbstractScrapper): Scrapper that will be used to obtain footprints from URL.
    """
    def __init__(self, url: str = None):
        if isurl_twitter(url):
            self.scrapper = TwitterScrapper(url)
        elif isurl_tiktok(url):
            self.scrapper = TiktokScrapper(url)
        elif isurl_github(url):
            self.scrapper = GithubScrapper(url)
        elif isurl_linkedin(url):
            self.scrapper = LinkedinScrapper(url)
        elif isurl_instagram(url):
            self.scrapper = InstagramScrapper(url)
        else:
            self.scrapper = GenericScrapper(url)
            

class AbstractScrapper(ABC):
    """ This class is responsible of defining the common behavior for the scrappers.

    Attributes:
        url (str): URL to scrap
        result (list): Found footprints.
    """
    def __init__(self, url: str):
        self.url = url
        self.result = self.scrap_data(url)

    @abstractmethod
    def scrap_data(self, url) -> list:
        return []

class TwitterScrapper(AbstractScrapper):
    """
    Class responsible of scrapping twitter
    """
    METHOD_NAME = "twitter_scrapper"

    def __init__(self, url: str):
        super().__init__(url)
        self.result = self.scrap_data(url)

    def scrap_data(self, url) -> list:
        """
        Retrieve data from twitter
        """
        result = []

        # Send a GET request to the URL
        response = requests.get(url.replace("mobile.", "").replace("twitter.com", "nitter.net"))

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the user's name
        if soup.find("a", {"class": "profile-card-fullname"}):
            result.append(
                {
                    "type" : "name",
                    "value" : soup.find("a", {"class": "profile-card-fullname"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's username
        if soup.find("a", {"class": "profile-card-username"}):
            result.append(
                {
                    "type" : "username",
                    "value" : soup.find("a", {"class": "profile-card-username"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's bio
        if soup.find("div", {"class": "profile-bio"}):
            result.append(
                {
                    "type" : "description",
                    "value" : soup.find("div", {"class": "profile-bio"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's location
        if soup.find("a", {"class": "profile-location"}):
            result.append(
                {
                    "type" : "location",
                    "value" : soup.find("a", {"class": "profile-location"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's website
        if soup.find("a", {"class": "profile-website"}):
            result.append(
                {
                    "type" : "url",
                    "value" : soup.find("a", {"class": "profile-website"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )


        # Find the user's birthdate
        if soup.find("a", {"class": "profile-birthdate"}):
            result.append(
                {
                    "type" : "birthdate",
                    "value" : soup.find("a", {"class": "profile-birthdate"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's profile pic URL
        if soup.find("a", {"class": "profile-card-avatar"}):
            result.append(
                {
                    "type" : "image",
                    "value" : soup.find("a", {"class": "profile-card-avatar"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )
        
        return result

class TiktokScrapper(AbstractScrapper):

    METHOD_NAME = "tiktok_scrapper"

    def __init__(self, url: str):
        super().__init__(url)
        if urlparse(url).path.startswith("/@"): # if it is a tiktok profile page
            self.result = self.scrap_data(url)
        else:
            self.result = []

    def scrap_data(self, url) -> list:
        result = []

        # Send a GET request to the URL
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the user's name
        if soup.find("h1", {"data-e2e": "user-subtitle"}):
            result.append(
                {
                    "type" : "name",
                    "value" : soup.find("h1", {"data-e2e": "user-subtitle"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's username
        if soup.find("h2", {"data-e2e": "user-title"}):
            result.append(
                {
                    "type" : "username",
                    "value" : soup.find("h2", {"data-e2e": "user-title"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's bio
        if soup.find("h2", {"data-e2e": "user-bio"}):
            result.append(
                {
                    "type" : "description",
                    "value" : soup.find("h2", {"data-e2e": "user-bio"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's website
        if soup.find("a", {"data-e2e": "user-link"}):
            result.append(
                {
                    "type" : "url",
                    "value" : soup.find("a", {"data-e2e": "user-link"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's profile pic URL
        if soup.find("div", {"data-e2e": "user-avatar"}):
            result.append(
                {
                    "type" : "image",
                    "value" : soup.find("div", {"data-e2e": "user-avatar"}).span.img["src"],
                    "method" : self.METHOD_NAME
                }
            )
        
        return result

class GithubScrapper(AbstractScrapper):

    METHOD_NAME = "github_scrapper"

    def __init__(self, url: str):
        super().__init__(url)
        self.result = self.scrap_data(url)

    def scrap_data(self, url) -> list:
        result = []

        # Send a GET request to the URL
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the user's name
        if soup.find("span", {"class": "vcard-fullname"}):
            result.append(
                {
                    "type" : "name",
                    "value" : soup.find("span", {"class": "vcard-fullname"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's username
        if soup.find("span", {"class": "vcard-username"}):
            result.append(
                {
                    "type" : "username",
                    "value" : soup.find("span", {"class": "vcard-username"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's bio
        if soup.find("div", {"class": "user-profile-bio"}):
            result.append(
                {
                    "type" : "description",
                    "value" : soup.find("div", {"class": "user-profile-bio"})["data-bio-text"],
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's location
        if soup.find("li", {"class": "vcard-detail", "itemprop": "homeLocation"}):
            result.append(
                {
                    "type" : "location",
                    "value" : soup.find("li", {"class": "vcard-detail", "itemprop": "homeLocation"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's website
        if soup.find("li", {"class": "vcard-detail", "itemprop": "url"}):
            result.append(
                {
                    "type" : "url",
                    "value" : soup.find("li", {"class": "vcard-detail", "itemprop": "url"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's profile pic URL
        if soup.find("img", {"class": "avatar-user"}):
            result.append(
                {
                    "type" : "image",
                    "value" : soup.find("img", {"class": "avatar-user"})["src"].split("?")[0],
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's social medias
        for s in (soup.find_all("li", {"class": "vcard-detail", "itemprop": "social"})) if soup.find_all("li", {"class": "vcard-detail", "itemprop": "url"}) else "":
            result.append(
                {
                    "type" : "url",
                    "value" : s.a["href"],
                    "method" : self.METHOD_NAME
                }
            )

        return result

class LinkedinScrapper(AbstractScrapper):

    METHOD_NAME = "linkedin_scrapper"

    def __init__(self, url: str):
        super().__init__(url)
        self.result = self.scrap_data(url)

    def scrap_data(self, url) -> list:
        result = []

        options = Options()
        options.add_argument("--headless")

        service = Service(executable_path=ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)
        driver.delete_all_cookies()
        #To be sure we have access to the linkedIn link, we are adding a referer header
        driver.get(url+"?original_referer=https%3A%2F%2Fwww.google.com%2F")
        driver.implicitly_wait(10)

        try:
            result.append(
                {
                    "type" : "name",
                    "value" : driver.find_element(By.CLASS_NAME, "top-card-layout__title").text,
                    "method" : self.METHOD_NAME
                }
            )
        except NoSuchElementException:
            pass

        try:
            result.append(
                {
                    "type" : "occupation",
                    "value" : driver.find_element(By.CLASS_NAME, "top-card-layout__headline").text,
                    "method" : self.METHOD_NAME
                }
            )
        except NoSuchElementException:
            pass

        try:
            result.append(
                {
                    "type" : "company",
                    "value" : driver.find_element(By.CLASS_NAME, "top-card__position-info").text,
                    "method" : self.METHOD_NAME
                }
            )
        except NoSuchElementException:
            pass

        try:
            result.append(
                {
                    "type" : "description",
                    "value" : driver.find_element(By.CLASS_NAME, "summary").find_element(By.TAG_NAME, "p").text,
                    "method" : self.METHOD_NAME
                }
            )
        except NoSuchElementException:
            pass

        driver.quit()
        return result
    
class InstagramScrapper(AbstractScrapper):

    METHOD_NAME = "instagram_scrapper"

    def __init__(self, url: str):
        super().__init__(url)
        self.result = self.scrap_data(url)

    def scrap_data(self, url) -> list:
        result = []

        # Send a GET request to the URL
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url.replace("instagram.com","picnob.com/profile"), headers=headers)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the user's name
        if soup.find("h1", {"class": "fullname"}):
            result.append(
                {
                    "type" : "name",
                    "value" : soup.find("h1", {"class": "fullname"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's username
        if soup.find("div", {"class": "username"}):
            result.append(
                {
                    "type" : "username",
                    "value" : soup.find("div", {"class": "username"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )

        # Find the user's bio
        if soup.find("div", {"class": "sum"}):
            result.append(
                {
                    "type" : "description",
                    "value" : soup.find("div", {"class": "sum"}).text.strip(),
                    "method" : self.METHOD_NAME
                }
            )
            
        return result

class GenericScrapper(AbstractScrapper):

    METHOD_NAME = "generic_scrapper"

    def __init__(self, url: str):
        super().__init__(url)
        self.result = self.scrap_data(url)

    def scrap_data(self, url) -> list:
        return []

def isurl_social(string: str, matching_urls: list[str]) -> bool:
    try:
        result = urlparse(string)
        if result.netloc in matching_urls:
            return True
        else:
            return False
    except ValueError:
        return False


def isurl_twitter(string):
    return isurl_social(string, ["twitter.com", "mobile.twitter.com"])

def isurl_instagram(string):
    return isurl_social(string, ["instagram.com", "www.instagram.com"])

def isurl_tiktok(string):
    return isurl_social(string, ["tiktok.com", "www.tiktok.com"])

def isurl_github(string):
    return isurl_social(string, ["github.com", "gist.github.com"])

def isurl_linkedin(string):
    return isurl_social(string, ["www.linkedin.com", "ad.linkedin.com", "ar.linkedin.com", "au.linkedin.com", "bb.linkedin.com", "bd.linkedin.com", "bm.linkedin.com", "bt.linkedin.com", "ca.linkedin.com", "cc.linkedin.com", "cg.linkedin.com", "ci.linkedin.com", "cn.linkedin.com", "co.linkedin.com", "cp.linkedin.com", "cv.linkedin.com", "de.linkedin.com", "dm.linkedin.com", "es.linkedin.com", "ew.linkedin.com", "fr.linkedin.com", "ge.linkedin.com", "gm.linkedin.com", "gs.linkedin.com", "gu.linkedin.com", "gw.linkedin.com", "hr.linkedin.com", "id.linkedin.com", "im.linkedin.com", "in.linkedin.com", "io.linkedin.com", "iq.linkedin.com", "is.linkedin.com", "it.linkedin.com", "ja.linkedin.com", "jp.linkedin.com", "la.linkedin.com", "lb.linkedin.com", "mc.linkedin.com", "md.linkedin.com", "me.linkedin.com", "ml.linkedin.com", "mm.linkedin.com", "ms.linkedin.com", "mx.linkedin.com", "my.linkedin.com", "nl.linkedin.com", "nt.linkedin.com", "oa.linkedin.com", "pg.linkedin.com", "pi.linkedin.com", "pm.linkedin.com", "pr.linkedin.com", "pt.linkedin.com", "qa.linkedin.com", "ra.linkedin.com", "rs.linkedin.com", "ru.linkedin.com", "sa.linkedin.com", "sc.linkedin.com", "sm.linkedin.com", "ss.linkedin.com", "st.linkedin.com", "sv.linkedin.com", "tv.linkedin.com", "tw.linkedin.com", "uk.linkedin.com", "us.linkedin.com", "vc.linkedin.com", "ws.linkedin.com"])
