"""
Class which represents an academic year.
"""

from bs4 import BeautifulSoup
from requests import Session

from course import Course
from exceptions.course_unavailable import CourseUnavailable


# Works
class Year:
    """
    all_courses: Get all visible courses in a year
    get_course: Get a course by name
    """

    def __init__(self, session: Session, start_year: int, end_year: int):
        self.start = start_year
        self.year = end_year
        self.url = f"https://themis.housing.rug.nl/course/{self.start}-{self.year}"
        self.__session = session

    # Method to get the courses of the year
    def all_courses(self, errors: bool = True) -> list[Course]:
        """
        all_courses(self, errors: bool = False) -> list[Course]
        Gets all visible courses in a year.
        Set errors to False to not raise an error when a course is unavailable.
        """
        r = self.__session.get(self.url)
        soup = BeautifulSoup(r.text, "lxml")
        lis = soup.find_all("li", class_="large")
        courses = []
        for li in lis:
            try:
                suffix = li.a["href"].replace(f"course/{self.start}-{self.year}", "")
                courses.append(
                    Course(self.url + suffix, li.a.text, self.__session, self)
                )
            except CourseUnavailable as exc:
                if errors:
                    raise CourseUnavailable(
                        message=f"Course {li.a.text} in year {self.start}-{self.year} unavailable"
                    ) from exc

                print("Error with course", li.a.text)
                continue

        return courses

    def get_course(self, name: str) -> Course:
        """
        get_course(self, name: str) -> Course
        Gets a course by name.
        """
        # Get the course
        r = self.__session.get(self.url)
        soup = BeautifulSoup(r.text, "lxml")
        # Search by name
        course = self.url + soup.find("a", text=name)["href"].replace(
            f"course/{self.start}-{self.year}", ""
        )
        # Get the url and transform it into a course object
        return Course(url=course, name=name, session=self.__session, parent=self)
