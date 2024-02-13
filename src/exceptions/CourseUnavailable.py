class CourseUnavailable(Exception):
  def __init__(self, message:str="Error in course"):
    self.message = message
    super().__init__(self.message)