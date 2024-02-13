# Noticed there's a similar pattern in the classes, so I'm going to create a base class for them

# classes that inherit from Base:
# - Course
# - Assignment
# - Exercise
from requests import Session
from bs4 import BeautifulSoup

class Base:
  def __init__(self, url:str, name:str, session:Session, parent):
    self.url = url
    self.name = name
    self.session = session
    self.parent = parent
 
  def __parseCfgBlock(self, div:BeautifulSoup) -> dict:
    # We assume that the div is a submission with class "cfg-container round"
    # Put each key and value in a dictionary
    # The key is a span with a class "cfg-key"
    # The value is a span with a class "cfg-val"

    # Get the key and value spans
    keys = div.find_all('span', class_="cfg-key")
    values = div.find_all('span', class_="cfg-val")

    # Create a dictionary
    submission = {}
    
    # Put each key and value in the dictionary
    for i in range(len(keys)):
      submission[keys[i].text] = values[i].text
    
    return submission 
  
  def getSubmissions(self):
    # We change the url where course becomes stats
    url = self.url.replace("course", "stats")
    r = self.session.get(url)

    # Get each div with class "cfg-container round"
    soup = BeautifulSoup(r.text, 'lxml')
    divs = soup.find_all('div', class_="cfg-container round")

    # The first one is an overview, the next ones are the submissions
    submissions = []
    for div in divs[1:]:
      submissions.append(self.__parseCfgBlock(div))
    return self.__parseCfgBlock(divs[0]), submissions

  def liLargeToAssignments(self, ul:BeautifulSoup) -> list:
    # Assume that ul is the block surrounding the li elements
    # Get all the li elements
    lis = ul.find_all('li', class_='large')
    # Turn each to an assignment instance
    assignments = [] 
    for li in lis:
      assignments.append(Base(li.a['href'], li.a.text, self.session, self.parent))
    return assignments

  def liLargeToExercises(self, ul:BeautifulSoup) -> list:
    # Assume that ul is the block surrounding the li elements
    # Get all the li elements
    lis = ul.find_all('li', class_='large')
    # Turn each to an exercise instance
    exercises = []
    for li in lis:
      exercises.append(Base(li.a['href'], li.a.text, self.session, self.parent))
    return exercises

  