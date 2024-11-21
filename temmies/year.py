from .course import Course
from bs4 import BeautifulSoup
class Year:
    """
    Represents an academic year.
    """
    def __init__(self, session, year_path: str):
        self.session = session
        self.year_path = year_path  # e.g., '2023-2024'
        self.base_url = "https://themis.housing.rug.nl"
        self.api_url = f"{self.base_url}/api/navigation/{self.year_path}"

    def all_courses(self) -> list:
        """
        Gets all visible courses in this year.
        """
        response = self.session.get(self.api_url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to retrieve courses for {self.year_path}.")

        courses_data = response.json()
        courses = []
        for course_info in courses_data:
            if course_info.get("visible", False):
                course_path = course_info["path"]
                course_title = course_info["title"]
                courses.append(Course(self.session, course_path, course_title, self))
        return courses

    def get_course(self, course_title: str) -> Course:
        """
        Gets a course by its title.
        """
        all_courses = self.all_courses()
        for course in all_courses:
            if course.title == course_title:
                return course
        raise ValueError(f"Course '{course_title}' not found in year {self.year_path}.")

    from bs4 import BeautifulSoup

    def get_course_by_tag(self, course_tag: str) -> Course:
        """
        Gets a course by its tag (course identifier).
        Constructs the course URL using the year and course tag.
        """
        course_path = f"/{self.year_path}/{course_tag}"
        course_url = f"{self.base_url}/course{course_path}"

        response = self.session.get(course_url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to retrieve course with tag '{course_tag}' for year {self.year_path}. Tried {course_url}")

        soup = BeautifulSoup(response.text, "lxml")

        title_elements = soup.find_all("a", class_="fill accent large")
        if title_elements:
            title_element = title_elements[-1]

        if title_element:
            course_title = title_element.get_text(strip=True)
        else:
            raise ValueError(f"Could not retrieve course title for tag '{course_tag}' in year {self.year_path}.")

        return Course(self.session, course_path, course_title, self)

    def __str__(self):
        return f"Year({self.year_path})"
