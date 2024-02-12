# Module to handle each assignment (most difficult part)

from Course import Course
from File import File
from Submission import Submission
from Base import Base
from Exercise import Exercise

class Assignment(Base):
  def __init__(self, url:str, name:str, session:Session, parent:Course):
    super().__init__()
    self.files = self.files

  def __str__(self):
    return f"Assignment {self.name} in course {self.parent.name}"

  
  def getSubmissions(self) -> Submission:
    pass

  def getExercises(self) -> list[Excercise]:
    pass
  
  def getExercise(self, name:str) -> Exercise:
    pass