# Class to handle courses
from bs4 import BeautifulSoup
from requests import Session
from ExerciseGroup import ExerciseGroup
import re
from exceptions.CourseUnavailable import CourseUnavailable

class Course:
  # Extend the Base class init
  def __init__(self, url:str, name:str, session:Session, parent):
    self.url = url
    self.name = name
    self.session = session
    self.parent = parent
    self.assignments = []
    self.__courseAvailable(self.session.get(self.url))

  def __str__(self):
    return f"Course {self.name} in year {self.parent.year}"
  
  def __courseAvailable(self, r):
    # Check if we got an error
    # print(self.url)
    if "Something went wrong" in r.text:
      raise CourseUnavailable(message="'Something went wrong'. Course most likely not found. ")
  
  @property
  def info(self):
    return {
      "name": self.name,
      "year": self.parent.year,
      "url": self.url,
      "assignments": [x.name for x in self.assignments]
    }

  def getExerciseGroups(self):
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    section = soup.find('div', class_="ass-children")
    entries = section.find_all('a', href=True)
    return [
      ExerciseGroup(
        f"https://themis.housing.rug.nl{x['href']}",
        x,
        self.session,
        self,
        ) 
      for x in entries]