# Year class to represent an academic year

from bs4 import BeautifulSoup
import selenium
from login import login
from Course import Course
from Themis import Themis
from Base import Base

class Year(Base):
  def __init__(name:str, session:Session, parent:Themis, end_year:int):
    super().__init__()
    self.start = end_year - 1
    self.year = end_year
    self.url = __constructUrl()

  # Method to set the url
  def __constructUrl(self):
    return f"https://themis.housing.rug.nl/{self.start}-{self.year}"

  # Method to get the courses of the year
  def getCourses(self) -> list[Course]:
    courses = []
    # TODO: Logic to get all courses
    return courses

  def getCourse(self, name:str) -> Course:
    #TODO: Implement
    pass