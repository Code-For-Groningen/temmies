# Classes
---

## `Themis`
Creates the initial connection to Themis.

### Usage
```python
from temmies.themis import Themis

themis = Themis("s-number")
```

On the first run, you will be prompted for your password. Then, on the next run(s), you will be able to log in automatically, as the password is stored in the system keyring. If you want to delete it [click here](https://www.google.com/search?hl=en&q=delete%20a%20password%20from%20keyring).

### Methods
#### `login()`
Logs in to Themis. Runs automatically when the class is initialized.

#### `get_year(start, end)`
Returns an instance of a [`Year`](#year) (academic year) between `start` and `end`.

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
assignments = pf.get_groups()
```

### Methods
#### `get_groups(full=False)`
Returns a list of `ExerciseGroup` instances corresponding to all exercise groups visible to the user in a given `Course`. The default argument is `full=False`, which will only return the top-level (name, link) of each exercise and folder in the group. If `full=True`, it will traverse the whole course.

You can traverse the course in both cases, although in different ways.

When you have fully traversed the course, you can access everything via indices and the `exercises` and `folders` attributes of the `ExerciseGroup` instances:

```python
ai_group = ai_course.get_groups(full=True)
exercise = ai_group[7].exercises[1]  # Week 11 -> Suitcase packing
exercise.submit(["suitcase.py"], silent=False)
```

This is equivalent to the case in which we don't traverse the whole course using `get_group` like so:

```python
ai_group = ai_course.get_group("Week 11")
exercise = ai_group.get_group("Suitcase packing")
exercise.submit(["suitcase.py"], silent=False)
```

#### `get_group(name, full=False)`
Returns an instance of an `ExerciseGroup` with the name `name`. The default argument is `full=False`, which will only return the (name, link) of each exercise and folder in the group. If `full=True`, it will traverse the whole group.

```python
week1 = pf.get_group("Week 1")
```

----

## `ExerciseGroup`
Setting the `full` flag to `True` will traverse the whole group.

- Both folders and exercises are represented as `ExerciseGroup` instances.
- Folders will have the `am_exercise` attribute set to `False`.
- Folders can have the `download_files` method called on them.
- Exercises can have the `submit`, `download_files`, and `download_tcs` methods called on them.

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
week1 = assignments[0]  # Week 1
exercise2 = week1.folders[1]  # Exercise 2
part2 = exercise2.exercises[1]  # Part 2

# Or, if you don't want to traverse the whole course:
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

#### `get_group(name, full=False)`
This is used when you want to traverse the course dynamically (not recurse through the whole thing). You can use it even if you've traversed the whole course.

```python
# Week 1 -> Exercise 2 -> Part 2
week1 = pf.get_group("Week 1")
exercise2 = week1.get_group("Exercise 2")
part2 = exercise2.get_group("Part 2")

# This is equivalent to (but faster than):
week1 = pf.get_groups(full=True)[0]
exercise2 = week1.folders[1]
part2 = exercise2.exercises[1]
```

#### `submit(files, judge=True, wait=True, silent=True)`
Submits the files to the exercise. The default arguments are `judge=True`, `wait=True`, and `silent=True`. Setting `judge=False` will not judge the submission immediately. Setting `wait=False` will not wait for the submission to finish. Turning off `silent` will print the submission status dynamically.

```python
suitcase = ai_course.get_group("Week 11").get_group("Suitcase packing")
suitcase.submit(["suitcase.py"], silent=False)

# Output:
# Submitting to Suitcase packing
# • suitcase.py
# 1: ✅
# 2: ✅
# 3: ✅
# ...
```

#### `get_status(text=False)`
Retrieves the status of the exercise group. When `text` is set to `True`, it will return the status as a dictionary of strings. Otherwise, it will return a dictionary where keys map to either strings or `Submission` objects. Common keys include `'leading'`, `'best'`, `'latest'`, etc.

```python
pf = year.get_course("Programming Fundamentals (for CS)")
exercise = pf.get_group("Lab Session 2").get_group("Recurrence")

# Get status
status = exercise.get_status()
print(status)

# Output:
{
  'assignment': 'Recurrence',
  'group': 'Y.N. Here',
  'status': 'passed: Passed all test cases',
  'grade': '2.00',
  'total': '2',
  'output limit': '1',
  'passed': '1',
  'leading': <temmies.submission.Submission object at 0x...>,
  'best': <temmies.submission.Submission object at 0x...>,
  'latest': <temmies.submission.Submission object at 0x...>,
  'first_pass': <temmies.submission.Submission object at 0x...>,
  'last_pass': <temmies.submission.Submission object at 0x...>,
  'visible': 'Yes'
}
```

To access submission details:

```python
leading_submission = status["leading"]
print(leading_submission.get_files())
```

----

## `Submission`
### Usage
```python
submission = pf.get_group("Week 1").get_group("Exercise 1").get_group("Part 1").get_status()["leading"]
```

### Methods
#### `get_test_cases()`
Returns a dictionary of test cases and their statuses.

```python
test_cases = submission.get_test_cases()
print(test_cases)

# Output:
{'1': 'passed', '2': 'passed', '3': 'passed', '4': 'passed', '5': 'passed', '6': 'passed', '7': 'passed', '8': 'passed', '9': 'passed', '10': 'passed'}
```

#### `get_info()`
Returns a dictionary of information about the submission.

```python
info = submission.get_info()
print(info)

# Output:
{
  'assignment': 'Part 1',
  'group': 'Y.N. Here',
  'uploaded_by': 'Y.N. Here s1234567',
  'created_on': 'Wed Sep 13 2023 12:51:37 GMT+0200',
  'submitted_on': 'Wed Sep 13 2023 12:51:37 GMT+0200',
  'status': 'passed: Passed all test cases',
  'files': [
    ('recurrence.c', '/file/.../recurrence.c'),
    ('compile.log', '/file/.../compile.log')
  ],
  'language': 'c'
}
```

#### `get_files()`
Returns a list of uploaded files in the format `(name, URL)`.

```python
files = submission.get_files()
print(files)

# Output:
[
  ('recurrence.c', '/file/.../recurrence.c'),
  ('compile.log', '/file/.../compile.log')
]
```

----
