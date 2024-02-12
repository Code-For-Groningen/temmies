# Class to handle courses
from bs4 import BeautifulSoup
from requests import Session
from Year import Year
from Assignment import Assignment
import re
from Base import Base

class Course(Base):
  def __init__(url:str, name:str, session:Session, parent:Year):
    super().__init__()
    self.url = self.__constructURL("name")
    self.assignments = []

  def __str__(self):
    return f"Course {self.name} in year {self.parent.year}"

  def __constructURL(self, name:str):
    # We have to find the name in the page and find its corresponding url
    r = self.session.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    # Find the course
    course = soup.find('a', text=self.name)
    # Get the url
    return course['href']
  
  @property
  def courseInfo(self):
    return {
      "name": self.name,
      "year": self.parent.year,
      "url": self.url,
      "assignments": [x.name for x in self.assignments]
    }

  def getAssignment(self, name:str) -> Assignment:
    # Optimization: if we already have the assignments, don't get them again
    try:
      if name in [x.name for x in self.assignments]:
        return name
    except AttributeError:
      pass

    # Get the assignment
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')

    # Search by name
    assignment = soup.find('a', text=name)
    # Get the url and transform it into an assignment object
    return Assignment(url=assignment['href'], name=name, session=self.session, course=self)


  def getAssignments(self) -> list[Assignment]:
    # For each link in the course page, get the assignment
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    # Find the assignments, they are in <li class="large">
    assignments = soup.find_all('li', class_='large')
    
    # FIXME: They sometimes put other stuff in these li's, so we have to filter them out

    # Create assignment object for each and store them in the class
    for assignment in assignments:
      # Get the name
      name = assignment.find('a').text
      # Get the url
      url = assignment.find('a')['href']
      # Create the object
      self.assignments.append(Assignment(url=url, name=name, session=self.session, course=self))
    

  def getGrades(self):
    pass

  