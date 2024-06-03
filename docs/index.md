# Temmies!
<center>![Temmie](img/rugemmie.gif)</center>


## What is this?
A python library which interacts with themis. Uses bs4. I'll try to end development on a somewhat working state. [Check out the code](https://github.com/Code-For-Groningen/temmies)

## Intended Features
* Log in
* Bulk download of test cases and files~~
* Submitting files
* Somewhat easy to use API to interact with courses

## Installation
```bash
pip install temmies
```

## Example Usage
```python
from temmies.themis import Themis

# Log in
themis = Themis("s-number", "password")

# Get a year
year = themis.get_year(2023, 2024)

# Get a course
course = year.get_course("Programming Fundamentals (for CS)")

# Get an assignment
assignment = course.get_group("Assignment 1")

# Submit 2 files
assignment.submit(["among.c", "us.py"])
```



