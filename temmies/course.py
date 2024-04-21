"""
Houses the Course class which is used to represent a course in a year.
"""

from bs4 import BeautifulSoup
from requests import Session

from .exercise_group import ExerciseGroup
from .exceptions.course_unavailable import CourseUnavailable
from .exceptions.illegal_action import IllegalAction


class Course:
    """
    get_groups: Get all groups in a course. Set full to True to get all subgroups.
    get_group: Get a group by name. Set full to True to get all subgroups.
    """

    def __init__(self, url: str, name: str, session: Session, parent):
        self.url = url
        self.name = name
        self.__session = session
        self.__parent = parent
        self.__request = self.__session.get(self.url)
        self.__raw = BeautifulSoup(self.__request.text, "lxml")

        self.__course_available(self.__session.get(self.url))

    def __str__(self):
        return f"Course {self.name} in year {self.__parent.year}"

    def __course_available(self, r):
        # Check if we got an error
        # print(self.url)
        if "Something went wrong" in r.text:
            raise CourseUnavailable(
                message="'Something went wrong'. Course most likely not found. "
            )

    def get_groups(self, full: bool = False) -> list[ExerciseGroup]:
        """
        get_groups(full: bool = False) -> list[ExerciseGroup]
        Get all groups in a course. Set full to True to get all subgroups.
        """
        section = self.__raw.find("div", class_="ass-children")
        entries = section.find_all("a", href=True)
        return [
            ExerciseGroup(
                f"https://themis.housing.rug.nl{x['href']}",
                x,
                self.__session,
                full
            )
            for x in entries
        ]

    # BAD: Repeated code!!!!
    def get_group(self, name: str, full: bool = False) -> ExerciseGroup:
        """
        get_group(name:str, full:bool = False) -> ExerciseGroup
        Get a single group by name. Set full to True to get all subgroups as well.
        """
        group = self.__raw.find("a", text=name)
        if not group:
            raise IllegalAction(message=f"No such group found: {name}")

        return ExerciseGroup(
            f"https://themis.housing.rug.nl{group['href']}",
            group,
            self.__session,
            full
        )
