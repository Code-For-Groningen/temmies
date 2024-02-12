# Module to handle files
from Base import Base
from Downloadable import Downloadable
from requests import Session

class File(Base):
  def __init__(self, url:str, name:str, session:Session, parent:Downloadable):
    super().__init__()

  def __str__(self):
    return f"File {self.name} for parent of Downloadable {self.parent.parent.name}"

  # I know this is reduntant, but how can you have a file class without a download()
  def download(self) -> str:
    r = self.session.get(self.url, stream=True)
    with open(self.name, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024):
        if chunk:
          f.write(chunk)
    return file.name

  def __eq__(self, other:File) -> bool:
    return self.name == other.name