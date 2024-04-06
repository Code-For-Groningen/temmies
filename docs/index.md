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
import temmies

# Log in
themis = temmies.Themis("s-number", "password")

# Get a year
year = themis.getYear(2023, 2024)

# Get a course
pf = year.getCourse("Programming Fundamentals (for CS)")

# Get an assignment
assignment = pf.getExerciseGroups()

# Download the files
assignment.downloadFiles()
```



