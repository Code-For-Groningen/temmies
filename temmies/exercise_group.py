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
            # Find using beautiful soup (it is the last a with class 'fill accent large')
            response = self.session.get(self.base_url + self.path)
            soup = BeautifulSoup(response.text, "lxml")
            title_elements = soup.find_all("a", class_="fill accent large")
            if title_elements:
                self.title = title_elements[-1].get_text(strip=True)
            else:
                self.title = self.path.split("/")[-1]
                
    def submit(self, files: list[str]) -> Submission:
        """
        Submit files to this exercise.
        """
        if not self.submitable:
            raise ValueError(f"Cannot submit to non-submittable item '{self.title}'.")

        # Prepare the files and data for submission
        files_payload = {}
        for idx, file_path in enumerate(files):
            file_key = f"file{idx}"
            with open(file_path, "rb") as f:
                files_payload[file_key] = (file_path, f.read())

        response = self.session.post(self.submit_url, files=files_payload)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to submit to '{self.title}'.")

        submission_data = response.json()
        return Submission(self.session, submission_data)

    def __str__(self):
        return f"ExerciseGroup({self.title})"
