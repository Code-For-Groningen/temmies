# Since we can download files both from the assignment itself and its exercises, this class will handle both

from requests import Session
from bs4 import BeautifulSoup
from Base import Base

class Downloadable(Base):
  def __init__(self, session:Session, parent):
    self.session = session
    self.parent = parent
    
  # File handling
  def __findFile(self, name:str):
    # Get the file by name
    for file in self.files:
      if file.name == name:
        return file
    return None

  @property
  def files(self) -> list:
    # Create a list of files
    # They are all links in a span with class "cfg-val"
    r = self.session.get(self.url)
    soup = BeautifulSoup(r.text, 'lxml')
    # Make sure we only get the ones that have a link
    # We parse the cfg and check for the key "Downloads"
    cfg = soup.find('div', class_='cfg-container round')
    cfg = self.__parseCfgBlock(cfg)
    # Get the downloads
    downloads = cfg.get("Downloads", None)
    if downloads == None:
      return []
    # Get the links
    links = downloads.find_all('a')
    files = []
    for link in links:
      files.append(File(link['href'], link.text, self.session, self))
    
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

