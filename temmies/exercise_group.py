from .group import Group
from .submission import Submission
from bs4 import BeautifulSoup

class ExerciseGroup(Group):
    """
    Represents a submittable exercise.
    """

    def __init__(self, session, path: str, title: str, parent, submitable: bool = True):
        super().__init__(session, path, title, parent, submitable=submitable)
        self.submit_url = f"{self.base_url}/api/submit{self.path}"
        self.__find_name()
    def __find_name(self):
        """
        Find the name of the exercise group.
        """
        if self.title == "":
            response = self.session.get(self.base_url + self.path)
            soup = BeautifulSoup(response.text, "lxml")
            title_elements = soup.find_all("a", class_="fill accent large")
            if title_elements:
                self.title = title_elements[-1].get_text(strip=True)
            else:
                self.title = self.path.split("/")[-1]

    def __str__(self):
        return f"ExerciseGroup({self.title})"
