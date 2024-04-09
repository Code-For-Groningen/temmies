from bs4 import BeautifulSoup
from exceptions.IllegalAction import IllegalAction
import re
from json import loads
from time import sleep


class ExerciseGroup:
    def __init__(self, url: str, soup, session, parent, full:bool):
        self.url = url
        self.name = soup.text
        self.__prev_raw = soup
        self.__session = session
        self.__request = self.__session.get(self.url)
        self.__raw = BeautifulSoup(self.__request.text, "lxml")
        self.__full = full


    @property
    def amExercise(self):
        return "ass-submitable" in self.__prev_raw["class"]

    def submit(self):
        if not self.amExercise:
            raise IllegalAction(message="You are submitting to a folder.")

        # Logic for submitting

    # Test cases
    @property
    def testCases(self):
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
        return None

    def downloadTCs(self, path="."):
        # Logic for downloading test cases(if any)
        # In a div with class "subsec round shade", where there is an h4 with text "Test cases"
        if not self.amExercise:
            raise IllegalAction(message="You are downloading test cases from a folder.")

        for tc in self.testCases:
            url = f"https://themis.housing.rug.nl{tc['href']}"

            print(f"Downloading {tc.text}")
            # download the files
            with open(f"{path}/{tc.text}", "wb") as f:
                f.write(self.__session.get(url).content)

        return self.testCases

    # Files
    @property
    def files(self):
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
                    for a in a:
                        link_list.append(a)

        return link_list if link_list else None

    def downloadFiles(self, path="."):
        for file in self.files:
            print(f"Downloading file {file.text}")
            url = f"https://themis.housing.rug.nl{file['href']}"
            with open(f"{path}/{file.text}", "wb") as f:
                f.write(self.__session.get(url).content)
        return self.files

    @property
    def exercises(self) -> list:
        if self.amExercise:
            return self

        section = self.__raw.find("div", class_="ass-children")
        try:
            submittables = section.find_all("a", class_="ass-submitable")
        except AttributeError:
            return None

        if not self.__full:
            return [(x.text,x['href']) for x in submittables]
        return [
            ExerciseGroup(
                f"https://themis.housing.rug.nl{x['href']}", x, self.__session, self, True
            )
            for x in submittables
        ]

    @property
    def folders(self) -> list:
        section = self.__raw.find("div", class_="ass-children")
        try:
            folders = section.find_all("a", class_="ass-group")
        except AttributeError:
            return None

        if not self.__full:
            return [(x.text,x['href']) for x in folders]
        
        return [
            ExerciseGroup(f"https://themis.housing.rug.nl{x['href']}", x, self.__session, self, True)
            for x in folders
        ]
    
    # Get by name
    def getGroup(self, name:str, full:bool=False, link:str=None):
        if link:
            return ExerciseGroup(link, self.__prev_raw, self.__session, self, full)
        
        group = self.__raw.find("a", text=name)
        if not group:
            raise IllegalAction(message=f"No such group found: {name}")
        
        return ExerciseGroup(f"https://themis.housing.rug.nl{group['href']}", group, self.__session, self, full)

    # Account for judge
    def __raceCondition(self, soup, url:str, verbose:bool):
      self.__session.get(url.replace("submission", "judge"))
      return self.__waitForResult(url, verbose, [])
    
    def __parseTable(self, soup, url:str, verbose:bool, __printed:list):
        cases = soup.find_all('tr', class_='sub-casetop')
        fail_pass = {}
        i = 1
        for case in cases:
          name = case.find('td', class_='sub-casename').text
          status = case.find('td', class_='status-icon')
          
          if "pending" in status.get("class"):
            return self.__raceCondition(soup,url,verbose)
          
          # queued status-icon
          if "queued" in status.get("class"):
            sleep(1) # <- 🗿
            return self.__waitForResult(url, verbose, __printed)
          
          if "Passed" in status.text:
            fail_pass[int(name)] = True
            if int(name) not in __printed and verbose == True:
              print(f"{name}: ✅")
          elif "Wrong output" in status.text:
            fail_pass[int(name)] = False
            if int(name) not in __printed and verbose == True:
              print(f"{name}: ❌")
          elif ("No status" or "error") in status.text:
            fail_pass[int(name)] = None
            if int(name) not in __printed and verbose == True: 
              print(f"{name}:🐛")
          
          __printed.append(int(name))
          i += 1
        return fail_pass
      
    def __waitForResult(self, url:str, verbose:bool, __printed:list):
        # This waits for result and returns a bundled info package
        r = self.__session.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        return self.__parseTable(soup, url, verbose, __printed)
        
        
    # Submit
    def submit(self, files: list, judge=True, wait=True, silent=True):

        # Find the form with submit and store the action as url
        # Store then the data-suffixes as file_types - dictionary

        form = self.__raw.find("form")
        if not form:
            raise IllegalAction(message="You cannot submit to this assignment.")

        url = "https://themis.housing.rug.nl" + form["action"]
        file_types = loads(form["data-suffixes"])

        if isinstance(files, str):
            temp = []
            temp.append(files)
            files = temp

        # Package the files up into files[]
        # DEBUG: Uncomment for better clarity
        # print("Submitting files:")
        # [print(f) for f in files]
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

            packaged_files.append((f"files[]", (file, open(file, "rb"), "text/x-csrc")))

        data = {"judgenow": "true" if judge else "false", "judgeLanguage": found_type}

        resp = self.__session.post(url, files=packaged_files, data=data)

        # Close each file
        i = 0
        for f in packaged_files:
          f[1][1].close()
          
        if not wait:
            return resp.url if "@submissions" in resp.url else None

        return self.__waitForResult(resp.url, not silent, [])
