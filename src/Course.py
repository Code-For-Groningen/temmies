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
    self.__session = session
    self.__parent = parent
    self.__request = self.__session.get(self.url)
    self.__raw = BeautifulSoup(self.__request.text, 'lxml')
    
    self.__courseAvailable(self.__session.get(self.url))

  def __str__(self):
    return f"Course {self.name} in year {self.__parent.year}"
  
  def __courseAvailable(self, r):
    # Check if we got an error
    # print(self.url)
    if "Something went wrong" in r.text:
      raise CourseUnavailable(message="'Something went wrong'. Course most likely not found. ")

  def getGroups(self, full:bool=False):
    section = self.__raw.find('div', class_="ass-children")
    entries = section.find_all('a', href=True)
    return [
      ExerciseGroup(
        f"https://themis.housing.rug.nl{x['href']}",
        x,
        self.__session,
        self,
        full
        ) 
      for x in entries]
  
  # BAD: Repeated code!!!!
  def getGroup(self, name:str, full:bool=False):
    group = self.__raw.find("a", text=name)
    if not group:
      raise IllegalAction(message=f"No such group found: {name}")
    
    return ExerciseGroup(f"https://themis.housing.rug.nl{group['href']}", group, self.__session, self, full)
