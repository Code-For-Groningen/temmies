"""
File to define the submission class
"""

from bs4 import BeautifulSoup

class Submission:
    """
    Submission class
    
    Methods:
    test_cases: Get a dict of test cases status
    info: Submission information (in details)
    files: Get a list of uploaded files(as names)
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
            return clean
        return clean.replace(" ", "_").replace(":", "").lower()

    def test_cases(self) -> dict[str, str]:
        """Get a dict of test cases status"""
        # In the submission page, the test cases are in a div with class "sub-cases subsec round shade"
        # print(self.__raw.prettify())
        cases = self.__raw.find("div", class_=lambda x: x and "sub-cases" in x.split())
        if not cases:
            return {}

        # The test cases are in a table in a div with class "cfg-container"
        cases = cases.find("div", class_="cfg-container")
        cases = cases.find("table")
        # For each test case, there is a tr with class sub-casetop, which contains 2 tds:
        # * a td with class "sub-case name" which is a name
        # * a td with a variable class, which is the status text

        results = {}
        for entry in cases.find_all("tr", class_="sub-casetop"):
            name = entry.find("td", class_="sub-casename").text
            status = entry.find(
                "td", class_=lambda x: x and "status-icon" in x.split()
            ).text
            results[name] = self.__clean(status)

        return results

    def info(self) -> dict[str, str] | None:
        """Submission information (in details)"""
        # in div with class subsec round shade where there is an h4 with class info
        # The info is in a div with class "cfg-container"
        if self.__info:
            return self.__info

        for div in self.__raw.find_all("div", class_="subsec round shade"):
            if h4 := div.find("h4", class_=lambda x: x and "info" in x.split()):
                if "Details" in h4.text:
                    # The information is in divs with class "cfg-line"
                    # With key in span with class "cfg-key" and value in span with class "cfg-value"
                    info = div.find("div", class_="cfg-container")
                    info = info.find_all("div", class_="cfg-line")
                    return {
                        self.__clean(
                            key := line.find("span", class_="cfg-key").text
                        ): 
                            self.__clean(line.find("span", class_="cfg-val").text, value=True) if "Files" not in key else 
                            ([(self.__clean(x.text), x["href"]) for x in line.find("span", class_="cfg-val").find_all("a")])
                        for line in info
                    }
        return None

    def files(self) -> list[str] | None:
        """Get a list of uploaded files in the format [(name, url)]"""
        if not self.__info:
            self.__info = self.info()
        
        return self.__info.get("files", None)
