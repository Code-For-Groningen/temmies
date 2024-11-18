"""
Main class for the Themis API using the new JSON endpoints.
"""

import keyring
import getpass
from requests import Session
from bs4 import BeautifulSoup
from .year import Year
from .exceptions.illegal_action import IllegalAction

class Themis:
    """
    Main class for interacting with Themis.
    - login: Login to Themis
    - get_year: Get a year object
    - all_years: Get all years
    """

    def __init__(self, user: str):
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
        self.user = user
        self.password = self.__get_password()
        self.base_url = "https://themis.housing.rug.nl"
        self.session = self.login(self.user, self.password)
    def __get_password(self) -> str:
        """
        Retrieve the password from the keyring, prompting the user if not found.
        """
        password = keyring.get_password(f"{self.user}-temmies", self.user)
        if not password:
            print(f"Password for user '{self.user}' not found in keyring.")
            password = getpass.getpass(prompt=f"Enter password for {self.user}: ")
            keyring.set_password(f"{self.user}-temmies", self.user, password)
            print("Password saved securely in keyring.")
        return password

    def login(self, user: str, passwd: str) -> Session:
        """
        Login to Themis using the original method, parsing CSRF token from the login page.
        """
        session = Session()
        login_url = f"{self.base_url}/log/in"

        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chromium/80.0.3987.160 Chrome/80.0.3987.163 Safari/537.36"
        )

        headers = {"user-agent": user_agent}

        data = {"user": user, "password": passwd, "null": None}

        # Get login page to retrieve CSRF token
        response = session.get(login_url, headers=headers, verify=False)
        if response.status_code != 200:
            raise ConnectionError("Failed to connect to Themis login page.")

        # Parse CSRF token from login page
        soup = BeautifulSoup(response.text, "lxml")
        csrf_input = soup.find("input", attrs={"name": "_csrf"})
        if not csrf_input or not csrf_input.get("value"):
            raise ValueError("Unable to retrieve CSRF token.")
        csrf_token = csrf_input["value"]
        data["_csrf"] = csrf_token
        data["sudo"] = user.lower()

        # Attempt login
        response = session.post(login_url, data=data, headers=headers)
        if "Invalid credentials" in response.text:
            # Prompt for password again
            print("Invalid credentials. Please try again.")
            passwd = getpass.getpass(prompt="Enter password: ")
            keyring.set_password(f'{self.user}-temmies', self.user, passwd)
            return self.login(user, passwd)
        elif "Welcome, logged in as" not in response.text:
            raise ValueError("Login failed for an unknown reason.")

        return session

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
