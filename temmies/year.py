from bs4 import BeautifulSoup
from .course import Course
from .exceptions.course_unavailable import CourseUnavailable

class Year:
    """
    Represents an academic year.
    """

    def __init__(self, session, start_year: int, end_year: int):
        self.start = start_year
        self.year = end_year
        self.url = f"https://themis.housing.rug.nl/course/{self.start}-{self.year}"
        self._session = session

    def all_courses(self, errors: bool = True) -> list[Course]:
        """
        Gets all visible courses in a year.
        """
        r = self._session.get(self.url)
        soup = BeautifulSoup(r.text, "lxml")
        lis = soup.find_all("li", class_="large")
        courses = []
        for li in lis:
            try:
                suffix = li.a["href"].replace(f"course/{self.start}-{self.year}", "")
                course_url = self.url + suffix
                course_name = li.a.text.strip()
                courses.append(
                    Course(course_url, course_name, self._session, self)
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
        Gets a course by name.
        """
        r = self._session.get(self.url)
        soup = BeautifulSoup(r.text, "lxml")
        course_link = soup.find("a", text=name)
        if not course_link:
            raise CourseUnavailable(f"No such course found: {name}")
        suffix = course_link["href"].replace(f"course/{self.start}-{self.year}", "")
        course_url = self.url + suffix
        return Course(course_url, name, self._session, self)
