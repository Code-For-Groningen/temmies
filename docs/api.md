# Classes
---
## `Themis`
Creates the initial connection to Themis.

### Usage
```python
from temmies.Themis import Themis

themis = Themis("s-number", "password")
```

### Methods
#### `login()`
Logs in to Themis. Runs automatically when the class is initialized.

#### `get_year(start, end)`
Returns an instance of a [`Year`](#year)(academic year) between `start` and `end`. 

```python
year = themis.get_year(2023, 2024)
```

#### `all_years()`
Returns a list of `Year` instances corresponding to all years visible to the user.

```python
years = themis.all_years()
```
<sub> I don't see why you would need this, but it's here. </sub>

----

## `Year`

### Usage
```python
year = themis.get_year(2023, 2024)
```

### Methods
#### `get_course(name)`
Returns an instance of a [`Course`](#course) with the name `name`.

```python
pf = year.get_course("Programming Fundamentals (for CS)")
```

#### `all_courses()`
Returns a list of `Course` instances corresponding to all courses visible to the user in a given `Year`.

```python
courses = year.all_courses()
```

----

## `Course`
### Usage
```python

pf = year.get_course("Programming Fundamentals (for CS)")
print(pf.info) # <- course info attribute
assignments = pf.get_groups()
```

### Methods
#### `get_groups(full=False)`
Returns a list of `ExerciseGroup` instances corresponding to all exercise groups visible to the user in a given `Course`. Default argument is `full=False`, which will only return the (name, link) of each exercise and folder in the group. If `full=True`, it will traverse the whole course.

You can traverse the course in both cases, although in different ways. 

When you have fully traversed the course, you can access everything via indices and the `exercises` and `folders` attributes of the `ExerciseGroup` instances:

```python
  ai_group = ai_course.get_groups(full=True)
  exercise = ai_group[7].exercises[1] # Week 11 -> Suitcase packing
  exercise.submit("suitcase.py", silent=False)```
```

This is equivalent to the case in which we don't traverse the full course using `get_group` like so:

```python
ai_group = ai_course.get_group("Week 11")
exercise = ai_group.get_group("Suitcase packing")
exercise.submit("suitcase.py", silent=False)
```

### `get_group(name, full=False)`
Returns an instance of an `ExerciseGroup` with the name `name`. Default argument is `full=False`, which will only return the (name, link) of each exercise and folder in the group. If `full=True`, it will traverse the whole group.

```python
week1 = pf.get_group("Week 1")
```

## `ExerciseGroup`
Setting the `full` flag to `True` will traverse the whole course. 

You can traverse the course in both cases
* Both folders and exercises are represented as `ExerciseGroup` instances.
* Folders will have the `am_exercise` attribute set to `False`.
* Folders can have the `download_files` method called on them.
* Exercises can have the `submit`, `download_files` and `download_tcs` method called on them.


### Example of folder traversal
Let's say we have a folder structure like this:
```
- Course Name
  - Week 1
    - Exercise 1
    - Exercise 2
      - Part 1
      - Part 2
  - Week 2
    - Exercise 1
    - Exercise 2
```
And we want to get to `Part 2` of `Week 1`'s `Exercise 2`. We would do this:

```python
pf = year.get_course("Programming Fundamentals (for CS)")
assignments = pf.get_groups()
week1 = assignments[0] # Week 1
exercise2 = week1.folders[1] # Exercise 2
part2 = exercise2.exercises[1] # Part 2

# Or, if you dont want to traverse the whole course:
week1 = pf.get_group("Week 1")
exercise2 = week1.get_group("Exercise 2")
part2 = exercise2.get_group("Part 2")
```


### Methods
#### `download_files(path=".")`
Downloads all files in the exercise group to a directory `path`. Defaults to the current directory.

```python
  assignment.download_files()
```

#### `download_tcs(path=".")`
Downloads all test cases in the exercise group to a directory `path`. Defaults to the current directory.

```python
  assignment.download_tcs()
```

#### get_group(name, full=False)
This is used when you want to traverse the course dynamically(not recurse through the whole thing). Of course, you can use it even if you've traversed the whole course, but that would overcomplicate things.

```python
  # Week 1 -> Exercise 2 -> Part 2
  week1 = pf.get_groups("Week 1")
  exercise2 = week1.get_group("Exercise 2")
  part2 = exercise2.get_group("Part 2")

  # This is equivalent to(but faster than):
  week1 = pf.get_groups("Week 1", full=True)
  exercise2 = week1[1]
  part2 = exercise2[1]
```


#### `submit(files)`
Submits the files to the exercise group. Default arguments are `judge=True`, `wait=True` and `silent=True`. `judge` will judge the submission instantly, and `wait` will wait for the submission to finish. Turning off `silent` will print the submission status dynamically.

```python
  suitcase = ai.get_group("Week 11")
  suitcase[7].exercises[1].submit("suitcase.py", silent=False)
  
  # Or
  ai.get_group("Week 11").get_group("Suitcase packing").submit("suitcase.py", silent=False)
  
  >>> 1: ✅
  >>> 2: ✅
  >>> 3: ✅
  >>> 4: ✅
  >>> 5: ✅
  >>> 6: ✅
  >>> 7: ✅
  >>> 8: ✅
  >>> 9: ✅
  >>> 10: ✅
  
```

#### `get_status(section=None, text=False)`
Parses the status of the exercise group(from a given section). If `section` is not `None`, it will return the status of the section. Don't set `section` if you don't know what you're doing.

When `text` is set to `True`, it will return the status as a dictionary of strings. Otherwise, it will return a tuple in the form `(dict(str:str), dict(str:Submission))`. Refer to the [Submission](#submission) class for more information.

```python
    pf = year.get_course("Programming Fundamentals (for CS)")
    pf_as = pf.get_group("Lab Session 2")
    
    # Get exercise
    exercise = pf_as.get_group("Recurrence")
    
    # Get status
    status = exercise.get_status()
    print(status)

  >>> (
  >>> { # Information [0]
  >>> 'assignment': 'Recurrence'
  >>> 'group': 'Y.N. Here'
  >>> 'status': 'passed: Passed all test cases'
  >>> 'grade': '2.00'
  >>> 'total': '2'
  >>> 'output limit': '1'
  >>> 'passed': '1'
  >>> 'leading': '/submission/2023-2024/progfun/lab2/recurrence/@submissions/s1234567/s1234567-1'
  >>> 'best': '/submission/2023-2024/progfun/lab2/recurrence/@submissions/s1234567/s1234567-1'
  >>> 'latest': '/submission/2023-2024/progfun/lab2/recurrence/@submissions/s1234567/s1234567-1'
  >>> 'first pass': '/submission/2023-2024/progfun/lab2/recurrence/@submissions/s1234567/s1234567-1'
  >>> 'last pass': '/submission/2023-2024/progfun/lab2/recurrence/@submissions/s1234567/s1234567-1'
  >>> 'visible': 'Yes'
  >>> }
  >>> { # Submission instances [1]
  >>> 'leading': <submission.Submission object at 0x774ea7a48cd0>
  >>> 'best': <submission.Submission object at 0x774ea79af910>
  >>> 'latest': <submission.Submission object at 0x774eaa7d3c10>
  >>> 'first_pass': <submission.Submission object at 0x774ea77ee810>
  >>> 'last_pass': <submission.Submission object at 0x774ea755de10>
  >>> }
  >>>)


```

#### `get_all_statuses(text=False)
Does the same as `get_status`, but for all visible status sections.


## `Submission`
### Usage
```python
submission = pf.get_group("Week 1").get_group("Exercise 1").get_group("Part 1").get_status()[1]["leading"]

```

### Methods
#### `test_cases()`
Returns a list of `TestCase` instances corresponding to all test cases in the submission.

```python
  submission = pf.get_group("Week 1").get_group("Exercise 1").get_group("Part 1").get_status()[1]["leading"]
  submission.test_cases()
```

#### `info()`
Returns a dictionary of information about the submission.

```python
  submission = pf.get_group("Week 1").get_group("Exercise 1").get_group("Part 1").get_status()[1]["leading"]
  submission.info()
```

#### `files()`
Returns a list of files in the form `(name, link)`.

```python
  submission = pf.get_group("Week 1").get_group("Exercise 1").get_group("Part 1").get_status()[1]["leading"]
  submission.files()
```

