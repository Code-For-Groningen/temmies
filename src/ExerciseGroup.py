from Base import Base
from bs4 import BeautifulSoup\

class ExerciseGroup(Base):
  # I can't tell if I'm already an exercise :C
  
  def __init__(self, url:str, name:str, session, parent):
    super().__init__(url, name, session, parent)
    self.exercises = self.getExercises()
    self.folders = self.getFolders()
    
  def __str__(self):
    return f"ExerciseGroup {self.name} in course {self.parent.name}"
  
  def getExercises(self) -> list:
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    section = soup.find('div', class_="ass-children")
    try:
      submittables = section.find_all('a', class_="ass-submitable")
    except AttributeError:
      return None
    
    return submittables
    
  # Returns a list of names of the folders
  def getFolders(self) -> list:
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    section = soup.find('div', class_="ass-children")
    try:
      folders = section.find_all('a', class_="ass-group")
    except AttributeError:
      return None
    
    return [x.text for x in folders]
  
  def recurse(self, folder:str):
    print(self.url)