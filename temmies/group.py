from bs4 import BeautifulSoup
from requests import Session
import os
from typing import Optional, Union, Dict
from .exceptions.illegal_action import IllegalAction
from .submission import Submission

class Group:
    """
    Represents an item in Themis, which can be either a folder (non-submittable) or an assignment (submittable).
    """

    def __init__(self, session, path: str, title: str, parent=None, submitable: bool = False):
        self.session = session
        self.path = path  # e.g., '/2023-2024/adinc-ai/labs'
        self.title = title
        self.parent = parent
        self.submitable = submitable
        self.base_url = "https://themis.housing.rug.nl"
        self.api_url = f"{self.base_url}/api/navigation{self.path}"
        self.classes = []

        # Adjust URL construction to include '/course' when accessing HTML pages
        if not self.path.startswith('/course/'):
            group_url = f"{self.base_url}/course{self.path}"
        else:
            group_url = f"{self.base_url}{self.path}"

        # Fetch the page and parse it
        response = self.session.get(group_url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to retrieve page for '{self.title}'. Tried {group_url}")
        self._raw = BeautifulSoup(response.text, "lxml")


    def get_items(self) -> list:
        """
        Get all items (groups and assignments) under this group.
        """
        section = self._raw.find("div", class_="ass-children")
        if not section:
            return []

        entries = section.find_all("a", href=True)
        items = []
        for x in entries:
            href = x['href']
            name = x.text.strip()
            classes = x.get('class', [])
            submitable = "ass-submitable" in classes
            item = Group(
                session=self.session,
                path=href,
                title=name,
                parent=self,
                submitable=submitable
            )
            items.append(item)
        return items

    def get_item_by_title(self, title: str):
        """
        Get a single item by its title, case-insensitive.
        """
        items = self.get_items()
        for item in items:
            if (item.title.lower() == title.lower()) or (item.path.split("/")[-1] == title):
                return item
        raise ValueError(f"Item '{title}' not found under {self.title}.")


    def get_status(self, text: bool = False) -> Union[Dict[str, Union[str, 'Submission']], None]:
        """
        Get the status of the current group, if available.
        """
        status_link = self._raw.find("a", text="Status")
        if not status_link:
            raise ValueError("Status information is not available for this group.")

        status_url = f"{self.base_url}{status_link['href']}"
        response = self.session.get(status_url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to retrieve status page for '{self.title}'.")

        soup = BeautifulSoup(response.text, "lxml")
        section = soup.find("div", class_="cfg-container")

        if not section:
            return None

        return self.__parse_status_section(section, text)

    def __parse_status_section(self, section: BeautifulSoup, text: bool) -> Dict[str, Union[str, 'Submission']]:
        """
        Parse the status section of the group and clean up keys.
        """
        key_mapping = {
            "leading the submission that counts towards the grade": "leading",
            "best the latest submission with the best result": "best",
            "latest the most recent submission": "latest",
            "first pass the first submission that passed": "first_pass",
            "last pass the last submission to pass before the deadline": "last_pass",
        }

        parsed = {}
        cfg_lines = section.find_all("div", class_="cfg-line")
        for line in cfg_lines:
            key_element = line.find("span", class_="cfg-key")
            value_element = line.find("span", class_="cfg-val")
            if not key_element or not value_element:
                continue

            # Normalize key
            raw_key = " ".join(key_element.get_text(separator=" ").strip().replace(":", "").lower().split())
            key = key_mapping.get(raw_key, raw_key)  # Use mapped key if available

            # Process value
            link = value_element.find("a", href=True)
            if link and not text:
                href = link["href"]
                # Construct full URL
                if href.startswith("/"):
                    submission_url = href
                elif href.startswith("http"):
                    submission_url = href.replace("https://themis.housing.rug.nl", "")
                else:
                    print(f"Invalid href '{href}' found in status page.")
                    continue  # Skip this entry if href is invalid

                # Instantiate Submission with submission_url and session
                submission = Submission(submission_url, self.session)
                parsed[key] = submission
            else:
                parsed[key] = value_element.get_text(separator=" ").strip()

        return parsed


    def get_test_cases(self) -> list[Dict[str, str]]:
        """
        Get all test cases for this assignment.
        """
        if not self.submitable:
            raise ValueError(f"No test cases for non-submittable item '{self.title}'.")

        sections = self._raw.find_all("div", class_="subsec round shade")
        tcs = []
        for div in sections:
            res = div.find("h4", class_="info")
            if res and "Test cases" in res.text:
                for case in div.find_all("div", class_="cfg-line"):
                    link = case.find("a")
                    if link:
                        tcs.append({
                            'title': link.text.strip(),
                            'path': link['href']
                        })
        return tcs

    def download_tcs(self, path=".") -> list[str]:
        """
        Download all test cases for this assignment.
        """
        test_cases = self.get_test_cases()
        downloaded = []
        for tc in test_cases:
            url = f"{self.base_url}{tc['path']}"
            print(f"Downloading {tc['title']}")
            response = self.session.get(url)
            if response.status_code == 200:
                tc_filename = os.path.join(path, tc['title'])
                with open(tc_filename, 'wb') as f:
                    f.write(response.content)
                downloaded.append(tc_filename)
            else:
                print(f"Failed to download test case '{tc['title']}'")
        return downloaded

    def get_files(self) -> list[Dict[str, str]]:
        """
        Get all downloadable files for this assignment.
        """
        details = self._raw.find("div", id=lambda x: x and x.startswith("details"))
        if not details:
            return []

        cfg_lines = details.find_all("div", class_="cfg-line")
        files = []

        for line in cfg_lines:
            key = line.find("span", class_="cfg-key")
            if key and "Downloads" in key.text.strip():
                vals = line.find_all("span", class_="cfg-val")
                for val in vals:
                    links = val.find_all("a")
                    for link in links:
                        files.append({
                            'title': link.text.strip(),
                            'path': link['href']
                        })
        return files

    def download_files(self, path=".") -> list[str]:
        """
        Download all files available for this assignment.
        """
        files = self.get_files()
        downloaded = []
        for file in files:
            print(f"Downloading file '{file['title']}'")
            url = f"{self.base_url}{file['path']}"
            response = self.session.get(url)
            if response.status_code == 200:
                file_filename = os.path.join(path, file['title'])
                with open(file_filename, 'wb') as f:
                    f.write(response.content)
                downloaded.append(file_filename)
            else:
                print(f"Failed to download file '{file['title']}'")
        return downloaded

    def submit(self, files: list[str], judge: bool = True, wait: bool = True, silent: bool = True) -> Optional[dict]:
        """
        Submit files to this assignment.
        Returns a dictionary of test case results or None if wait is False.
        """
        if not self.submitable:
            raise ValueError(f"Cannot submit to non-submittable item '{self.title}'.")

        form = self._raw.find("form")
        if not form:
            raise ValueError("Submission form not found.")

        url = f"{self.base_url}{form['action']}"
        file_types = loads(form.get("data-suffixes", "{}"))

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
            print(f"Submitting to {self.title}")
            for file in files:
                print(f"• {file}")

        resp = self.session.post(url, files=packaged_files, data=data)

        if not wait or not judge:
            return resp.url if "@submissions" in resp.url else None

        return self.__wait_for_result(resp.url, not silent, [])

    def __wait_for_result(self, url: str, verbose: bool, __printed: list) -> dict:
        """
        Wait for the submission result and return the test case results.
        """
        r = self.session.get(url)
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

    def __str__(self):
        return f"Group({self.title}, submitable={self.submitable})"
