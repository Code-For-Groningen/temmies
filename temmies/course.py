from .group import Group
from .exercise_group import ExerciseGroup
from requests import Session
from .exceptions.course_unavailable import CourseUnavailable

class Course(Group):
    """
    Represents a course in a given academic year.
    """

    def __init__(self, url: str, name: str, session, parent):
        super().__init__(url, name, session, parent=parent, full=False)
        self.__course_available(self._request)

    def __str__(self):
        return f"Course {self.name} in year {self._parent.year}"

    def __course_available(self, response):
        if "Something went wrong" in response.text:
            raise CourseUnavailable(
                message="'Something went wrong'. Course most likely not found."
            )

    def create_group(self, url: str, name: str, session: Session, parent, full: bool, classes=None):
        """
        Create an instance of ExerciseGroup for subgroups within a Course.
        """
        return ExerciseGroup(url, name, session, parent, full, classes)
