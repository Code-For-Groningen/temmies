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

#### `get_year(year_path)`
Returns an instance of a [`Year`](#year) for the academic year specified by `year_path`.

```python
year = themis.get_year(2023, 2024)
```

#### `all_years()`
Returns a list of `Year` instances corresponding to all years visible to the user.

```python
years = themis.all_years()
```

----

## `Year`

### Usage
```python
year = themis.get_year(2023, 2024)
```

### Methods
#### `get_course(course_title)`
Returns an instance of a [`Course`](#course) with the title `course_title`.

```python
pf = year.get_course("Programming Fundamentals (for CS)")
```

#### `get_course_by_tag(course_tag)`
Returns an instance of a [`Course`](#course) using the course identifier `course_tag`.

```python
ai_course = year.get_course_by_tag("adinc-ai")
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
Returns a list of `ExerciseGroup` or `Group` instances corresponding to all items visible to the user in a given `Course`. The default argument is `full=False`, which will only return the top-level (name, link) of each item. If `full=True`, it will traverse the whole course.

```python
ai_groups = ai_course.get_groups(full=True)
exercise = ai_groups[7].exercises[1]
exercise.submit(["solution.py"], silent=False)
```

#### `get_group(name, full=False)`
Returns an instance of an `ExerciseGroup` or `Group` with the name `name`. The default argument is `full=False`, which will only return the (name, link) of the group. If `full=True`, it will traverse the whole group.

```python
week1 = pf.get_group("Week 1")
```

#### `create_group(item_data)`
Creates and returns a `Group` or `ExerciseGroup` instance based on `item_data`.

```python
group = course.create_group(item_data)
```

----

## `Group`

Represents an item in Themis, which can be either a folder (non-submittable) or an assignment (submittable).

### Methods
#### `get_items()`
Returns all items (groups and assignments) under this group.

```python
items = week1.get_items()
```

#### `get_item_by_title(title)`
Returns a single item by its title (case-insensitive).

```python
item = week1.get_item_by_title("Exercise 2")
```

#### `get_status(text=False)`
Retrieves the status of the group. When `text=True`, returns the status as strings. Otherwise, returns submission objects or strings.

```python
status = group.get_status()
leading_submission = status["leading"]
```

#### `download_files(path=".")`
Downloads all files available for this group to a directory `path`. Defaults to the current directory.

```python
group.download_files()
```

#### `download_tcs(path=".")`
Downloads all test cases for this group to a directory `path`. Defaults to the current directory.

```python
group.download_tcs()
```

#### `submit(files, judge=True, wait=True, silent=True)`
Submits the files to the group. Default arguments are `judge=True`, `wait=True`, and `silent=True`.

```python
group.submit(["solution.py"], silent=False)
```

----

## `ExerciseGroup`
Represents a submittable exercise. Inherits from `Group`.

### Additional Methods
#### `submit(files)`
Submits files to the exercise. Raises an error if the item is not submittable.

```python
exercise.submit(["solution.py"])
```

----

## `Submission`

Represents a submission for a specific exercise.

### Methods
#### `get_test_cases()`
Returns a dictionary of test cases and their statuses.

```python
test_cases = submission.get_test_cases()
```

#### `get_info()`
Returns detailed information about the submission.

```python
info = submission.get_info()
```

#### `get_files()`
Returns a list of uploaded files in the format `(name, URL)`.

```python
files = submission.get_files()
```
