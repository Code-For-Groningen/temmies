# temmies/group.py

from bs4 import BeautifulSoup
from requests import Session
from typing import Optional, Union, Dict
from .exceptions.illegal_action import IllegalAction
from .submission import Submission


class Group:
    """
    Base class for Course and ExerciseGroup.
    """

    def __init__(self, url: str, name: str, session: Session, parent=None, full: bool = False, classes=None):
        self.url = url
        self.name = name
        self._session = session
        self._parent = parent
        self._full = full
        self._request = self._session.get(self.url)
        self._raw = BeautifulSoup(self._request.text, "lxml")
        self.classes = classes or []

    def __str__(self):
        return f"Group {self.name}"

    def get_groups(self, full: bool = False):
        """
        Get all groups (exercises and folders) within this group.
        """
        section = self._raw.find("div", class_="ass-children")
        if not section:
            return []

        entries = section.find_all("a", href=True)
        groups = []
        for x in entries:
            href = x['href']
            name = x.text.strip()
            classes = x.get('class', [])
            group = self.create_group(
                url=f"https://themis.housing.rug.nl{href}",
                name=name,
                session=self._session,
                parent=self,
                full=full,
                classes=classes
            )
            groups.append(group)
        return groups

    def get_group(self, name: str, full: bool = False):
        """
        Get a single group by name.
        """
        group_link = self._raw.find("a", text=name)
        if not group_link:
            raise IllegalAction(f"No such group found: {name}")
        href = group_link['href']
        classes = group_link.get('class', [])
        return self.create_group(
            url=f"https://themis.housing.rug.nl{href}",
            name=name,
            session=self._session,
            parent=self,
            full=full,
            classes=classes
        )

    def create_group(self, url: str, name: str, session: Session, parent, full: bool, classes=None):
        """
        Factory method to create a group. Subclasses must implement this.
        """
        raise NotImplementedError("Subclasses must implement create_group")

    def get_status(self, text: bool = False) -> Union[Dict[str, Union[str, Submission]], None]:
        """
        Get the status of the current group, if available.

        Args:
            text (bool): If True, returns text representation of the status.
                        Otherwise, creates `Submission` objects for applicable fields.

        Returns:
            dict[str, Union[str, Submission]] | None: The status data for the group, 
                                                    with `Submission` objects for links.
        """
        status_link = self._raw.find("a", text="Status")
        if not status_link:
            raise IllegalAction("Status information is not available for this group.")

        status_url = f"https://themis.housing.rug.nl{status_link['href']}"
        r = self._session.get(status_url)
        soup = BeautifulSoup(r.text, "lxml")
        section = soup.find("div", class_="cfg-container")

        if not section:
            return None

        return self.__parse_status_section(section, text)

    def __parse_status_section(self, section: BeautifulSoup, text: bool) -> Dict[str, Union[str, Submission]]:
        """
        Parse the status section of the group and clean up keys.

        Args:
            section (BeautifulSoup): The HTML section containing the status information.
            text (bool): Whether to return text representation.

        Returns:
            dict[str, Union[str, Submission]]: Parsed and cleaned status information,
                                            with `Submission` objects for links.
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
                submission_url = link["href"]
                parsed[key] = Submission(submission_url, self._session)
            else:
                parsed[key] = value_element.get_text(separator=" ").strip()

        return parsed
