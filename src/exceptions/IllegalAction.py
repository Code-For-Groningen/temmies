class IllegalAction(Exception):
  def __init__(self, message:str=""):
    self.message = "Illegal action: " + message
    super().__init__(self.message)