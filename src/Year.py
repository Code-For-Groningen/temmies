# Year class to represent an academic year

from bs4 import BeautifulSoup
from Course import Course
from requests import Session
from exceptions.CourseUnavailable import CourseUnavailable

class Year:
  def __init__(self, session:Session, parent, start_year:int, end_year:int):
    self.start = start_year
    self.year = end_year
    self.session = session
    self.url = self.__constructUrl()

  # Method to set the url
  def __constructUrl(self):
    return f"https://themis.housing.rug.nl/course/{self.start}-{self.year}"

  # Method to get the courses of the year
  def getCourses(self, errors:bool=False) -> list[Course]:
    # lis in a big ul 
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    lis = soup.find_all('li', class_='large')
    courses = []
    for li in lis:
      try:
        courses.append(
          Course(
            self.url + li.a['href'],
            li.a.text,
            self.session,
            self
          )
        )
      except CourseUnavailable:
        if errors:
          raise CourseUnavailable(f"Course {li.a.text} in year {self.start}-{self.year} is not available")
        else:
          pass
      
      
    return courses

  def getCourse(self, name:str) -> Course:
    # Get the course
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    # Search by name
    course = soup.find('a', text=name)
    # Get the url and transform it into a course object
    return Course(url=course['href'], name=name, session=self.session, year=self)