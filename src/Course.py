# Class to handle courses
from bs4 import BeautifulSoup
from requests import Session
from Assignment import Assignment
import re
from Base import Base
from exceptions.CourseUnavailable import CourseUnavailable

# PROBLEM: This implementation is bad due to inconsistencies in the website 
# The way we can tell the difference between an assignment and an exercise is by the presence of an a with the class "ass-submitable" 
# As opposed to folders which contain exercises which are marked with "ass-group"
# Therefore, we should take that into consideration and spawn the corresponding Exercise or Assignment class
# Naming becomes a bit inconsistent like that as well, as Assignments could be Exercises. Might opt to call the "assignments" "exerciseGroups" or some shit.

class Course(Base):
  # Extend the Base class init
  def __init__(self, url:str, name:str, session:Session, parent):
    super().__init__(url, name, session, parent)
    self.assignments = []
    self.__courseAvailable(self.session.get(self.url))

  def __str__(self):
    return f"Course {self.name} in year {self.parent.year}"
  
  def __courseAvailable(self, r):
    # Check if we got an error
    print(self.url)
    if "Something went wrong" in r.text:
      raise CourseUnavailable()
  
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
    return Assignment(url=assignment['href'], name=name, session=self.session, parent=self)


  def getAssignments(self) -> list[Assignment]:
    # For each link in the course page, get the assignment
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    # Find the big ul
    # print(soup)
    section = soup.find('div', class_="ass-children")
    ul = section.find('ul', class_='round')
    
    # IDEA: They sometimes put other stuff in these li's, so we have to filter them out
    # print(ul)
    # print(type(ul))
    # Transform them into Assignment objects
    # I want to call the __liLargeToAssignments method from the Base class
    return self.liLargeToAssignments(ul)