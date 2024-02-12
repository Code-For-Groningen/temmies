# Noticed there's a similar pattern in the classes, so I'm going to create a base class for them

from requests import Session

class Thing:
  def __init__(url:str, name:str, session:Session, parent:Class):
    self.url = url
    self.name = name
    self.session = session
    self.parent = parent