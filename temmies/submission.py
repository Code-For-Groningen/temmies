# submission.py

"""
File to define the Submission class
"""

from bs4 import BeautifulSoup

class Submission:
    """
    Submission class

    Methods:
    get_test_cases: Get a dict of test cases status
    get_info: Submission information (in details)
    get_files: Get a list of uploaded files (as names)
    """
    def __init__(self, url: str, session):
        self.url = "https://themis.housing.rug.nl" + url
        self.__session = session
        self.__request = self.__session.get(self.url)
        self.__raw = BeautifulSoup(self.__request.text, "lxml")
        self.__info = None

    def __clean(self, text: str, value: bool = False) -> str:
        """Clean text"""
        clean = text.replace("\t", "").replace("\n", "")
        if value:
            return clean.strip()
        return clean.replace(" ", "_").replace(":", "").lower().strip()

    def get_test_cases(self) -> dict[str, str]:
        """Get a dict of test cases status"""
        cases = self.__raw.find("div", class_=lambda x: x and "sub-cases" in x.split())
        if not cases:
            return {}

        cases = cases.find("div", class_="cfg-container")
        cases = cases.find("table")

        results = {}
        for entry in cases.find_all("tr", class_="sub-casetop"):
            name = entry.find("td", class_="sub-casename").text
            status = entry.find(
                "td", class_=lambda x: x and "status-icon" in x.split()
            ).text
            results[name.strip()] = self.__clean(status)

        return results

    def get_info(self) -> dict[str, str] | None:
        """Submission information (in details)"""
        if self.__info:
            return self.__info

        for div in self.__raw.find_all("div", class_="subsec round shade"):
            h4 = div.find("h4", class_=lambda x: x and "info" in x.split())
            if h4 and "Details" in h4.text:
                info = div.find("div", class_="cfg-container")
                info_lines = info.find_all("div", class_="cfg-line")
                self.__info = {
                    self.__clean(
                        key := line.find("span", class_="cfg-key").text
                    ): (
                        self.__clean(line.find("span", class_="cfg-val").text, value=True)
                        if "Files" not in key
                        else [
                            (self.__clean(a.text), a["href"])
                            for a in line.find("span", class_="cfg-val").find_all("a")
                        ]
                    )
                    for line in info_lines
                }
                return self.__info
        return None

    def get_files(self) -> list[str] | None:
        """Get a list of uploaded files in the format [(name, url)]"""
        if not self.__info:
            self.__info = self.get_info()
        return self.__info.get("files", None)

    # Deprecated methods
    def info(self):
        print("This method is deprecated and will be deleted soon. Use get_info instead.")
        return self.get_info()

    def test_cases(self):
        print("This method is deprecated and will be deleted in soon. Use get_test_cases instead.")
        return self.get_test_cases()

    def files(self):
        print("This method is deprecated and will be deleted in soon. Use get_files instead.")
        return self.get_files()
