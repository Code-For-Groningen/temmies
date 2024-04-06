from bs4 import BeautifulSoup
from exceptions.IllegalAction import IllegalAction
import re 

class ExerciseGroup():
  def __init__(self, url:str, soup, session, parent):
    self.url = url
    self.name = soup.text
    self.__raw = soup
    self.session = session
    self.parent = parent # This is unnecessary, but I'll keep it for now
    self.request = self.session.get(self.url)
    self.soup = BeautifulSoup(self.request.text, 'lxml')
    
  def __str__(self):
    return f"ExerciseGroup {self.name} in folder {self.parent.name}"
  
  @property
  def amExercise(self):
    return "ass-submitable" in self.__raw['class']
  
  def submit(self):
    if not self.amExercise:
      raise IllegalAction(message="You are submitting to a folder.")
    
    # Logic for submitting
  
  # Test cases
  @property
  def testCases(self):
    section = self.soup.find_all('div', class_="subsec round shade")
    tcs = []
    for div in section:
      res = div.find("h4", class_="info")
      if not res:
        continue
      
      if "Test cases" in res.text:
        for case in div.find_all("div", class_="cfg-line"):
          if link := case.find("a"):
            tcs.append(link)
        return tcs
    return None
  
  def downloadTCs(self, path="."):
    # Logic for downloading test cases(if any)
    # In a div with class "subsec round shade", where there is an h4 with text "Test cases"
    if not self.amExercise:
      raise IllegalAction(message="You are downloading test cases from a folder.")
  
    for tc in self.testCases:
      url= f"https://themis.housing.rug.nl{tc['href']}"
      
      print(f"Downloading {tc.text}")
      # download the files
      with open(f"{path}/{tc.text}", "wb") as f:
        f.write(self.session.get(url).content)
    
    return self.testCases
  
  # Files
  @property
  def files(self):
    details = self.soup.find('div', id=lambda x: x and x.startswith('details'))
        
    cfg_lines = details.find_all('div', class_='cfg-line')
    
    link_list = []
    
    for line in cfg_lines:
      key = line.find('span', class_='cfg-key')
      
      if key and "Downloads" in key.text.strip():
        # Extract all links in the cfg-val span
        links = line.find_all('span', class_='cfg-val')
        for link in links:
          a = link.find_all('a')
          for a in a:
            link_list.append(a)
    
    return link_list if link_list else None


  
  def downloadFiles(self, path="."):
    for file in self.files:
      print(f"Downloading file {file.text}")
      url = f"https://themis.housing.rug.nl{file['href']}"
      with open(f"{path}/{file.text}", "wb") as f:
        f.write(self.session.get(url).content)
    return self.files
  
  # idea exercises and folders are identical, maybe merge them?
  @property
  def exercises(self) -> list:
    if self.amExercise:
      return self
      
    section = self.soup.find('div', class_="ass-children")
    try:
      submittables = section.find_all('a', class_="ass-submitable")
    except AttributeError:
      return None
    
    return [
      ExerciseGroup(f"https://themis.housing.rug.nl{x['href']}",
                    x,
                    self.session,
                    self)
      for x in submittables]
    
  @property
  def folders(self) -> list:
    section = self.soup.find('div', class_="ass-children")
    try:
      folders = section.find_all('a', class_="ass-group")
    except AttributeError:
      return None
    
    return [
      ExerciseGroup(f"https://themis.housing.rug.nl{x['href']}",
                    x,
                    session,
                    self)
      for x in folders]
  