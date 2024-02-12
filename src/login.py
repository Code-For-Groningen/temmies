# Module to handle login
# URL to login: https://themis.housing.rug.nl/log/in
# POST request which contains the following data:
# - username
# - password
# - null

from requests import post
from bs4 import BeautifulSoup

