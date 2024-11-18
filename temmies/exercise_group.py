from .group import Group
from .exceptions.illegal_action import IllegalAction
from .submission import Submission
from json import loads
from time import sleep
from typing import Optional
from bs4 import BeautifulSoup


class ExerciseGroup(Group):
    """
    Represents a group of exercises or a single exercise.
    """

    def __init__(self, url: str, name: str, session, parent=None, full: bool = False, classes=None):
        super().__init__(url, name, session, parent=parent, full=full, classes=classes)
        self.am_exercise = "ass-submitable" in self.classes

    def create_group(self, url: str, name: str, session, parent, full: bool, classes=None):
        """
        Create an instance of ExerciseGroup for subgroups.
        """
        return ExerciseGroup(url, name, session, parent, full, classes)

    @classmethod
    def create_group_from_url(cls, url: str, full: bool) -> 'ExerciseGroup':
        """
        Create an instance of ExerciseGroup from a full URL of a Themis group.
        This method will retrieve the name of the group from the URL.

        Args:
            url (str): URL of the Themis group.
            full (bool): Whether to traverse the whole group.

        Returns:
            ExerciseGroup: An instance of ExerciseGroup.
        """
        if "https://themis.housing.rug.nl/course/" not in url:
            url = "https://themis.housing.rug.nl/course/" + url

        # Find name of group (last of a with class fill accent large)
        r = cls._session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        group_links = soup.find_all("a", class_="fill accent large")
        name = group_links[-1].text

        return cls(url, name, cls._session, parent=None, full=full)

    @property
    def test_cases(self) -> list[str]:
        """
        Get all test cases for this exercise.
        """
        if not self.am_exercise:
            return []

        sections = self._raw.find_all("div", class_="subsec round shade")
        tcs = []
        for div in sections:
            res = div.find("h4", class_="info")
            if res and "Test cases" in res.text:
                for case in div.find_all("div", class_="cfg-line"):
                    if link := case.find("a"):
                        tcs.append(link)
        return tcs

    def download_tcs(self, path=".") -> list[str]:
        """
        Download all test cases for this exercise.
        """
        if not self.am_exercise:
            raise IllegalAction(
                "You are downloading test cases from a folder.")

        for tc in self.test_cases:
            url = f"https://themis.housing.rug.nl{tc['href']}"
            print(f"Downloading {tc.text}")
            with open(f"{path}/{tc.text}", "wb") as f:
                f.write(self._session.get(url).content)
        return self.test_cases

    @property
    def files(self) -> list[str]:
        """
        Get all downloadable files for this exercise or group.
        """
        details = self._raw.find(
            "div", id=lambda x: x and x.startswith("details"))
        if not details:
            return []

        cfg_lines = details.find_all("div", class_="cfg-line")
        link_list = []

        for line in cfg_lines:
            key = line.find("span", class_="cfg-key")
            if key and "Downloads" in key.text.strip():
                links = line.find_all("span", class_="cfg-val")
                for link in links:
                    a_tags = link.find_all("a")
                    for a in a_tags:
                        link_list.append(a)
        return link_list

    def download_files(self, path=".") -> list[str]:
        """
        Download all files available for this exercise or group.
        """
        for file in self.files:
            print(f"Downloading file {file.text}")
            url = f"https://themis.housing.rug.nl{file['href']}"
            with open(f"{path}/{file.text}", "wb") as f:
                f.write(self._session.get(url).content)
        return self.files

    def submit(self, files: list[str], judge: bool = True, wait: bool = True, silent: bool = True) -> Optional[dict]:
        """
        Submit files to this exercise.
        Returns a dictionary of test case results or None if wait is False.
        """
        if not self.am_exercise:
            raise IllegalAction("You cannot submit to this assignment.")

        form = self._raw.find("form")
        if not form:
            raise IllegalAction("Submission form not found.")

        url = "https://themis.housing.rug.nl" + form["action"]
        file_types = loads(form["data-suffixes"])

        if isinstance(files, str):
            files = [files]

        packaged_files = []
        data = {}
        found_type = ""

        for file in files:
            for suffix, lang in file_types.items():
                if file.endswith(suffix):
                    found_type = lang
                    break
            if not found_type:
                print("WARNING: File type not recognized")

            with open(file, "rb") as f:
                packaged_files.append((found_type, (file, f.read())))

        data = {
            "judgenow": "true" if judge else "false",
            "judgeLanguage": found_type if found_type else "none"
        }

        if not silent:
            print(f"Submitting to {self.name}")
            for file in files:
                print(f"• {file}")

        resp = self._session.post(url, files=packaged_files, data=data)

        if not wait or not judge:
            return resp.url if "@submissions" in resp.url else None

        return self.__wait_for_result(resp.url, not silent, [])

    def __wait_for_result(self, url: str, verbose: bool, __printed: list) -> dict:
        """
        Wait for the submission result and return the test case results.
        """
        r = self._session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        return self.__parse_table(soup, url, verbose, __printed)

    def __parse_table(self, soup: BeautifulSoup, url: str, verbose: bool, __printed: list) -> dict:
        """
        Parse the results table from the submission result page.
        """
        cases = soup.find_all("tr", class_="sub-casetop")
        fail_pass = {}
        for case in cases:
            name = case.find("td", class_="sub-casename").text
            status = case.find("td", class_="status-icon")

            if "pending" in status.get("class"):
                sleep(1)
                return self.__wait_for_result(url, verbose, __printed)

            statuses = {
                "Passed": ("✅", True),
                "Wrong output": ("❌", False),
                "No status": ("🐛", None),
                "error": ("🐛", None),
            }

            found = False
            for k, v in statuses.items():
                if k in status.text:
                    found = True
                    if verbose and int(name) not in __printed:
                        print(f"{name}: {v[0]}")
                    fail_pass[int(name)] = v[1]
                    break
            if not found:
                fail_pass[int(name)] = None
                if verbose and int(name) not in __printed:
                    print(f"{name}: Unrecognized status: {status.text}")

            __printed.append(int(name))
        return fail_pass
