# Module to handle each assignment (most difficult part)

from Downloadable import Downloadable
from Base import Base
from Exercise import Exercise
from requests import Session

class Assignment(Base):
  def __init__(self, url:str, name:str, session:Session, parent):
    super().__init__()
    self.download = Downloadable(url, name, session, self)

  def __str__(self):
    return f"Assignment {self.name} in course {self.parent.name}"  

  def getExercises(self) -> list[Exercise]:
    # Find li large
    ul = self.soup.find('ul', class_='round')

    # Turn each li to an exercise instance
    return self.liLargeToExercises(ul, self.session, self)
  
  def getExercise(self, name:str) -> Exercise:
    # Get the exercise
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    # Search by name
    exercise = soup.find('a', text=name)
    # Get the url and transform it into an exercise object
    return Exercise(url=exercise['href'], name=name, session=self.session, assignment=self)