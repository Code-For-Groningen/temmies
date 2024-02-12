# Module to handle login
# URL to login: https://themis.housing.rug.nl/log/in
# POST request which contains the following data:
# - username
# - password
# - null

from requests import Session
from bs4 import BeautifulSoup
from config import username, password
import urllib3

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to login to Themis
def login(user, passwd):
  headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/80.0.3987.160 Chrome/80.0.3987.163 Safari/537.36"
 }

  data = {
    "user": username,
    "password":password,
    "null": None
  }
  
  with Session() as s:
    url = 'https://themis.housing.rug.nl/log/in'
    r = s.get(url,headers=headers,verify=False)
    soup = BeautifulSoup(r.text, 'lxml')

    # get the csrf token and add it to payload
    csrfToken = soup.find('input',attrs = {'name':'_csrf'})['value']
    data['_csrf'] = csrfToken

    # Login
    r = s.post(url,data=data,headers = headers)
    
    # check if login was successful
    log_out = "Welcome, logged in as" in r.text
    if log_out:
      print(f"Login for user {username} successful")
    else:
      print("Login failed")
      return None 
  
  return s


if __name__ == "__main__":
  print("Do not run this module like this. Used to give a logged in session.")