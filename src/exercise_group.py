"""
Houses the ExerciseGroup class.
Represents a group of exercises or a single exercise.

"""

from json import loads
from time import sleep
from bs4 import BeautifulSoup
from exceptions.illegal_action import IllegalAction


class ExerciseGroup:
    """
    am_exercise: returns bool which tells you if the instance is an exercise
    submit: submit to an exercise
    get_group: get a group by name
    get_groups: get all groups
    folders: folders in the folder
    exercises: exercises in the folder
    test_cases: test cases in the exercise(if it is an exercise)
    download_tcs: download test cases
    files: files in the exercise/folder
    download_files: download files
    """

    def __init__(self, url: str, soup, session, full: bool):
        self.url = url
        self.name = soup.text
        self.__prev_raw = soup
        self.__session = session
        self.__request = self.__session.get(self.url)
        self.__raw = BeautifulSoup(self.__request.text, "lxml")
        self.__full = full

    @property
    def am_exercise(self) -> bool:
        return "ass-submitable" in self.__prev_raw["class"]

    # Test cases
    @property
    def test_cases(self) -> list[str]:
        section = self.__raw.find_all("div", class_="subsec round shade")
        tcs = []
        for div in section:
            res = div.find("h4", class_="info")
            if not res:
                continue

            if "Test cases" in res.text:
                for case in div.find_all("div", class_="cfg-line"):
                    if link := case.find("a"):
                        tcs.append(link)
        return tcs

    def download_tcs(self, path=".") -> list[str]:
        """
        download_tcs(path=".") -> list[str]
        Downloads every test case available from a given exercise. `path` defaults to '.'.
        """
        if not self.am_exercise:
            raise IllegalAction(message="You are downloading test cases from a folder.")

        for tc in self.test_cases:
            url = f"https://themis.housing.rug.nl{tc['href']}"

            print(f"Downloading {tc.text}")
            # download the files
            with open(f"{path}/{tc.text}", "wb") as f:
                f.write(self.__session.get(url).content)

        return self.test_cases

    # Files
    @property
    def files(self) -> list[str]:
        details = self.__raw.find("div", id=lambda x: x and x.startswith("details"))

        cfg_lines = details.find_all("div", class_="cfg-line")

        link_list = []

        for line in cfg_lines:
            key = line.find("span", class_="cfg-key")

            if key and "Downloads" in key.text.strip():
                # Extract all links in the cfg-val span
                links = line.find_all("span", class_="cfg-val")
                for link in links:
                    a = link.find_all("a")
                    for i in a:
                        link_list.append(i)

        return link_list

    def download_files(self, path=".") -> list[str]:
        """
        download_files(path=".") -> list[str]
        Downloads every file available from a given exercise/folder. `path` defaults to '.'.
        """
        for file in self.files:
            print(f"Downloading file {file.text}")
            url = f"https://themis.housing.rug.nl{file['href']}"
            with open(f"{path}/{file.text}", "wb") as f:
                f.write(self.__session.get(url).content)
        return self.files

    @property
    def exercises(self) -> list[str] | list["ExerciseGroup"]:
        if self.am_exercise:
            return self

        section = self.__raw.find("div", class_="ass-children")
        try:
            submittables = section.find_all("a", class_="ass-submitable")
        except AttributeError:
            return []

        if not self.__full:
            return [(x.text, x["href"]) for x in submittables]
        return [
            ExerciseGroup(
                f"https://themis.housing.rug.nl{x['href']}", x, self.__session, True
            )
            for x in submittables
        ]

    @property
    def folders(self) -> list[str] | list["ExerciseGroup"]:
        section = self.__raw.find("div", class_="ass-children")
        try:
            folders = section.find_all("a", class_="ass-group")
        except AttributeError:
            return []

        if not self.__full:
            return [(x.text, x["href"]) for x in folders]

        return [
            ExerciseGroup(
                f"https://themis.housing.rug.nl{x['href']}", x, self.__session, True
            )
            for x in folders
        ]

    # Get by name
    def get_group(
        self, name: str, full: bool = False, link: str = None
    ) -> "ExerciseGroup":
        """
        get_group(name:str, full:bool=False, link:str=None) -> ExerciseGroup | list[ExerciseGroup]
        Get a single group by name.
        Set `full` to True to get all subgroups as well.
        Set `link` to directly fetch a group.
        """
        if link:
            return ExerciseGroup(link, self.__prev_raw, self.__session, full)

        group = self.__raw.find("a", text=name)
        if not group:
            raise IllegalAction(message=f"No such group found: {name}")

        return ExerciseGroup(
            f"https://themis.housing.rug.nl{group['href']}", group, self.__session, full
        )

    # Wait for result
    def __wait_for_result(self, url: str, verbose: bool, __printed: list) -> None:
        # This waits for result and returns a bundled info package
        r = self.__session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        return self.__parse_table(soup, url, verbose, __printed)

    # Account for judge
    def __race_condition(self, url: str, verbose: bool) -> None:
        self.__session.get(url.replace("submission", "judge"))
        return self.__wait_for_result(url, verbose, [])

    def __parse_table(
        self, soup: BeautifulSoup, url: str, verbose: bool, __printed: list
    ) -> dict:
        cases = soup.find_all("tr", class_="sub-casetop")
        fail_pass = {}
        i = 1
        for case in cases:
            name = case.find("td", class_="sub-casename").text
            status = case.find("td", class_="status-icon")

            if "pending" in status.get("class"):
                return self.__race_condition(url, verbose)

            # queued status-icon
            if "queued" in status.get("class"):
                sleep(1)  # <- 🗿
                return self.__wait_for_result(url, verbose, __printed)

            statuses = {
                "Passed": ("✅", True),
                "Wrong output": ("❌", False),
                "No status": ("🐛", None),
                "error": ("🐛", None),
            }

            # Printing and storing
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
            i += 1
        return fail_pass

    # Submit
    def submit(
        self, files: list, judge: bool = True, wait: bool = True, silent: bool = True
    ) -> dict | None:
        """
        submit(files:list, judge:bool=True, wait:bool=True, silent:bool=True) -> dict | None
        Submits given files to given exercise. Returns a dictionary of test cases and their status.
        Set judge to False to not judge the submission.
        Set wait to False to not wait for the result.
        Set silent to False to print the results.
        """
        form = self.__raw.find("form")
        if not form:
            raise IllegalAction(message="You cannot submit to this assignment.")

        url = "https://themis.housing.rug.nl" + form["action"]
        file_types = loads(form["data-suffixes"])

        if isinstance(files, str):
            temp = []
            temp.append(files)
            files = temp

        packaged_files = []
        data = {}
        found_type = ""
        for file in files:
            for t in file_types:
                if t in file:
                    found_type = file_types[t]
                    break
            if not found_type:
                raise IllegalAction(message="Illegal filetype for this assignment.")

            with open(file, "rb") as f:
                packaged_files.append((found_type, (file, f.read())))

        data = {"judgenow": "true" if judge else "false", "judgeLanguage": found_type}

        if not silent:
            print(f"Submitting to {self.name}")
            for file in files:
                print(f"• {file}")
        resp = self.__session.post(url, files=packaged_files, data=data)

        if not wait or not judge:
            return resp.url if "@submissions" in resp.url else None

        return self.__wait_for_result(resp.url, not silent, [])
