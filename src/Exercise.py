from Base import Base
from Downloadable import Downloadable
from requests import Session

from time import sleep


class Exercise(Base):
  def __init__(self, url:str, name:str, session:Session, parent):
    super().__init__()
    self.download = Downloadable(url, name, session, self)

  def __str__(self):
    return f"Exercise {self.name} in assignment {self.parent.name}"

  # IDEA : Make this async, so we don't have to wait for the whole output to load
  def submit(self, file:str, comment:str) -> str:
    # Submit a file
    # The form is in the page with class "cfg-container round"
    # The form is a POST request to the url with the file and the comment
    # The url looks like this: https://themis.housing.rug.nl/submit/{year}/{course}/{assignment}/{exercise}?_csrf={session_csrf}&sudo={username}
    # The current url looks like: https://themis.housing.rug.nl/course/{year}/{course}/{assignment}/{exercise}
    # The request should contain the contents of the file

    # Get the url
    url = self.url.replace("course", "submit")
    # Get the csrf token
    csrf = self.session.cookies['_csrf']
    # Get the username
    username = self.session.cookies['username']
    
    # Open the file
    with open(file, 'rb') as f:
      # Submit the file
      # After submission it will 302 to the current submission page
      r = self.session.post(url, files={'file': f}, data={'comment': comment, '_csrf': csrf, 'sudo': username})
      
      # Follow the redirect and repeatedly send get requests to the page
      
      # We have a table which represents the test cases. The program should wait until all the test cases are done
      # The test case is done when all of the elements in the table are not none
      # The element which showcases this for each <tr class="sub-casetop">
      # is the class in there. if it is "queued" it is still running.

      # Get the url
      url = r.url
      # Get the page
      r = self.session.get(url)
      # Get the soup
      soup = BeautifulSoup(r.text, 'lxml')
      # Get the table
      table = soup.find('table')
      # Get the rows
      rows = table.find_all('tr', class_='sub-casetop')
      # Get the status
      status = [row.find('td', class_='status').text for row in rows]
      # Wait until all the status are not queued
      while "queued" in status:
        # Wait a bit
        sleep(1)
        # Get the page
        r = self.session.get(url)
        # Get the soup
        soup = BeautifulSoup(r.text, 'lxml')
        # Get the table
        table = soup.find('table')
        # Get the rows
        rows = table.find_all('tr', class_='sub-casetop')


    pass