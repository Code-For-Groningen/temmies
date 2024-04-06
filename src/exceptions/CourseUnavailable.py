class CourseUnavailable(Exception):
  def __init__(self, message:str=""):
    self.message = "Course Error: " + message
    super().__init__(self.message)