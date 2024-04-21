"""
Main class for the Themis API

"""

import urllib3
from requests import Session
from bs4 import BeautifulSoup
from .year import Year
from .exceptions.illegal_action import IllegalAction


# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Themis:
    """
    login: Login to Themis
    get_year: Get a year object
    all_years: Get all years
    """

    def __init__(self, user: str, passwd: str):
        self.session = self.login(user, passwd)
        self.years = []
        self.url = "https://themis.housing.rug.nl/course/"

    def login(self, user: str, passwd: str) -> Session:
        """
        login(self, user: str, passwd: str) -> Session
        Login to Themis
        Set user to your student number and passwd to your password
        """

        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chromium/80.0.3987.160 Chrome/80.0.3987.163 Safari/537.36"
        )

        headers = {"user-agent": user_agent}

        data = {"user": user, "password": passwd, "null": None}

        with Session() as s:
            url = "https://themis.housing.rug.nl/log/in"
            r = s.get(url, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "lxml")

            # get the csrf token and add it to payload
            csrf_token = soup.find("input", attrs={"name": "_csrf"})["value"]
            data["_csrf"] = csrf_token
            data["sudo"] = user.lower()

            # Login
            r = s.post(url, data=data, headers=headers)

            # check if login was successful
            log_out = "Welcome, logged in as" in r.text
            if not log_out:
                raise IllegalAction(message=f"Login for user {user} failed")

        return s

    def get_year(self, start: int, end: int) -> Year:
        """
        get_year(self, start: int, end: int) -> Year
        Gets a year object
        Set start to the start year and end to the end year (e.g. 2023-2024)
        """
        return Year(self.session, start, end)

    def all_years(self) -> list[Year]:
        """
        get_years(self, start: int, end: int) -> list[Year]
        Gets all visible years
        """
        # All of them are in a big ul at the beginning of the page
        r = self.session.get(self.url)
        soup = BeautifulSoup(r.text, "lxml")
        ul = soup.find("ul", class_="round")
        lis = ul.find_all("li", class_="large")
        years = []
        for li in lis:
            # format: 2019-2020
            year = li.a.text.split("-")
            years.append(Year(self.session, int(year[0]), int(year[1])))

        return years  # Return a list of year objects
