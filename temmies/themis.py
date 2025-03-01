"""
Main class for the Themis API using the new JSON endpoints.
"""

from requests import Session
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
        Login to Themis by spawning a selenium browser
        """
        login_url = f"{self.base_url}/login"
        driver = webdriver.Chrome()

        driver.get(login_url)

        wait = WebDriverWait(driver, 60)

        try:
            wait.until(EC.url_contains("signon.rug.nl/nidp/saml2/sso"))
            current_url = driver.current_url

            # If on the sign-on page fill in the credentials
            if "signon.rug.nl/nidp/saml2/sso" in current_url:
                user_field = wait.until(EC.presence_of_element_located((By.NAME, "Ecom_User_ID")))
                pass_field = wait.until(EC.presence_of_element_located((By.NAME, "Ecom_Password")))
                
                if self.user and not user_field.get_attribute("value"):
                    user_field.clear()
                    user_field.send_keys(self.user)
                if self.password and not pass_field.get_attribute("value"):
                    pass_field.clear()
                    pass_field.send_keys(self.password)
            
            # THIS IS LIKELY TO BREAK AT SOME POINT
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Cannot GET"))
            
        except TimeoutException:
            print("Timeout waiting for login/2FA page to load.")
        except (NoSuchElementException, StaleElementReferenceException) as e:
            print(f"Encountered an error: {e}")
        finally:
            # security
            self.password = "I-HAVE-BEEN-REMOVED"
            cookies = driver.get_cookies()
            driver.quit()

        # Add all cookies to the session.
        for cookie in cookies:
            session.cookies.set(name=cookie["name"], value=cookie["value"])

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
