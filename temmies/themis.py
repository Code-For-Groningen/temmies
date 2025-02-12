"""
Main class for the Themis API using the new JSON endpoints.
"""

from requests import Session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from json import dumps
from .year import Year
import getpass
import keyring

class Themis:
    """
    Main class for interacting with Themis.
    - login: Login to Themis
    - get_year: Get a year object
    - all_years: Get all years
    """

    def __init__(self, cookies: dict = None, user=None):
        """
        Initialize Themis object, logging in with the given user.

        Args:
            user (str): Username to login with.

        Attributes:
            user (str): Username.
            password (str): Password, retrieved from keyring.
            base_url (str): Base URL of the Themis website.
            session (requests.Session): Authenticated session.
        """
        self.base_url = "https://themis.housing.rug.nl"
        self.session = self._setup_agent()
        
        self.user, self.password = None, None
        
        # Old login logic
        if user:
            self.user = user
            self.password = self._get_password()
        
        # Reusing session logic
        if not cookies:
            self.session = self.login(self.session)
        else:
            self.session.cookies.update(cookies)
            if not self.check_session():
                self.session = self.login(self.session)
    
    def _get_password(self) -> str:
        """
        Retrieve the password from the keyring, prompting the user if not found.
        """
        password = keyring.get_password(f"{self.user}-temmies", self.user)
        if not password:
            print(f"Password for user '{self.user}' not found in keyring.")
            password = getpass.getpass(
                prompt=f"Enter password for {self.user}: ")
            keyring.set_password(f"{self.user}-temmies", self.user, password)
            print("Password saved securely in keyring.")
        return password

    def _setup_agent(self) -> Session:

        session = Session()

        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chromium/80.0.3987.160 Chrome/80.0.3987.163 Safari/537.36"
        )

        session.headers.update({"User-Agent": user_agent})

        return session

    def check_session(self) -> bool:
        """
        Check if the session is still valid.
        """
        
        # look at the /login and find a pre tag
        login_url = f"{self.base_url}/login"
        response = self.session.get(login_url)
        return "pre" in response.text
    
        
    def login(self, session: Session) -> Session:
        """
        Login to Themis by spawning a selenium browser, logging in and storing the session.
        """

        login_url = f"{self.base_url}/login"

        # Start a full browser to login
        driver = webdriver.Chrome()

        driver.get(login_url)

        while True:
            if driver.find_elements(By.TAG_NAME, "pre"):
                break
            
            try:
                # if any of the fields are already filled, don't fill them
                if  (passw := driver.find_element(By.NAME, "Ecom_Password")) and not passw.get_attribute("value") and self.password:
                    passw.send_keys(self.password)
                if  (user := driver.find_element(By.NAME, "Ecom_User_ID")) and not user.get_attribute("value") and self.user:
                    user.send_keys(self.user)
                
            except NoSuchElementException:
                pass
            
            except StaleElementReferenceException:
                pass
        
        # destroy the password from memory (security)
        self.password = "I-HAVE-BEEN-REMOVED"
        
        # export all stored cookies
        cookies = driver.get_cookies()
        driver.quit()

        # add all cookies to the session
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"])

        return session

    def get_session_cookies(self):
        """
        Get the session cookies in json
        """
        return dumps(self.session.cookies.get_dict())

    def get_year(self, start_year: int = None, end_year: int = None) -> Year:
        """
        Gets a Year object using the year path (e.g., 2023, 2024).
        """
        year_path = f"{start_year}-{end_year}"

        return Year(self.session, year_path)

    def all_years(self) -> list:
        """
        Gets all visible years as Year objects.
        """
        navigation_url = f"{self.base_url}/api/navigation/"
        response = self.session.get(navigation_url)
        if response.status_code != 200:
            raise ConnectionError("Failed to retrieve years from Themis API.")

        years_data = response.json()
        years = []
        for year_info in years_data:
            if year_info.get("visible", False):
                year_path = year_info["path"].strip("/")
                years.append(Year(self.session, year_path))
        return years
