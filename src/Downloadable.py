# Since we can download files both from the assignment itself and its exercises, this class will handle both

from requests import Session
from bs4 import BeautifulSoup

class Downloadable:
  def __init__(self, session:Session, parent:Class):
    self.session = session
    self.parent = parent
    
  # File handling
  def __findFile(self, name:str) -> File:
    # Get the file by name
    for file in self.files:
      if file.name == name:
        return file
    return None

  @property
  def files(self) -> list[File]:
    # Create a list of files
    # They are all in a span with class "cfg-val"
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    spans = soup.find_all('span', class_="cfg-val")
    # Get the links and names of the files, create a File object for each
    files = [File(url=a['href'], name=a.text, session=self.session, parent=self) for a in spans]
  return files

  def download(self, filename:str) -> str:
    # Download the file
    if filename == None:
      raise NameError("No filename provided")

    file = self.__findFile(filename)
    r = self.session.get(file.url, stream=True)
    with open(file.name, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024):
        if chunk:
          f.write(chunk)
    return file.name
  
  def downloadAll(self) -> list[str]:
    # Download all files
    return [self.download(file.name) for file in self.files]

