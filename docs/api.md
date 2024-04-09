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

#### `getYear(start, end)`
Returns an instance of a [`Year`](#year)(academic year) between `start` and `end`. 

```python
year = themis.getYear(2023, 2024)
```

#### `allYears()`
Returns a list of `Year` instances corresponding to all years visible to the user.

```python
years = themis.allYears()
```
<sub> I don't see why you would need this, but it's here. </sub>

----

## `Year`

### Usage
```python
year = themis.getYear(2023, 2024)
```

### Methods
#### `getCourse(courseName)`
Returns an instance of a [`Course`](#course) with the name `courseName`.

```python
pf = year.getCourse("Programming Fundamentals (for CS)")
```

#### `allCourses()`
Returns a list of `Course` instances corresponding to all courses visible to the user in a given `Year`.

```python
courses = year.allCourses()
```

----

## `Course`
### Usage
```python

pf = year.getCourse("Programming Fundamentals (for CS)")
print(pf.info) # <- course info attribute
assignments = pf.getGroups()
```

### Methods
#### `getGroups(full=False)`
Returns a list of `ExerciseGroup` instances corresponding to all exercise groups visible to the user in a given `Course`. Default argument is `full=False`, which will only return the (name, link) of each exercise and folder in the group. If `full=True`, it will traverse the whole course.

You can traverse the course in both cases, although in different ways. 

When you have fully traversed the course, you can access everything via indices and the `exercises` and `folders` attributes of the `ExerciseGroup` instances:

```python
  ai_group = ai_course.getGroups(full=True)
  exercise = ai_group[7].exercises[1] # Week 11 -> Suitcase packing
  exercise.submit("suitcase.py", silent=False)```
```

This is equivalent to the case in which we don't traverse the full course using `getGroup` like so:

```python
ai_group = ai_course.getGroup("Week 11")
exercise = ai_group.getGroup("Suitcase packing")
exercise.submit("suitcase.py", silent=False)
```

### `getGroup(name, full=False)`
Returns an instance of an `ExerciseGroup` with the name `name`. Default argument is `full=False`, which will only return the (name, link) of each exercise and folder in the group. If `full=True`, it will traverse the whole group.

```python
week1 = pf.getGroup("Week 1")
```

## `ExerciseGroup`
Setting the `full` flag to `True` will traverse the whole course. 

You can traverse the course in both cases
* Both folders and exercises are represented as `ExerciseGroup` instances.
* Folders will have the `amExercise` attribute set to `False`.
* Folders can have the `downloadFiles` method called on them.
* Exercises can have the `submit`, `downloadFiles` and `downloadTCs` method called on them.


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
pf = year.getCourse("Programming Fundamentals (for CS)")
assignments = pf.getExerciseGroups()
week1 = assignments[0] # Week 1
exercise2 = week1.folders[1] # Exercise 2
part2 = exercise2.exercises[1] # Part 2

# Or, if you dont want to traverse the whole course:
week1 = pf.getGroup("Week 1")
exercise2 = week1.getGroup("Exercise 2")
part2 = exercise2.getGroup("Part 2")
```


### Methods
#### `downloadFiles(path=".")`
Downloads all files in the exercise group to a directory `path`. Defaults to the current directory.

```python
  assignment.downloadFiles()
```

#### `downloadTCs(path=".")`
Downloads all test cases in the exercise group to a directory `path`. Defaults to the current directory.

```python
  assignment.downloadTCs()
```

#### getGroup(name, full=False)
This is used when you want to traverse the course dynamically(not recurse through the whole thing). Of course, you can use it even if you've traversed the whole course, but that would overcomplicate things.

```python
  # Week 1 -> Exercise 2 -> Part 2
  week1 = pf.getGroups("Week 1")
  exercise2 = week1.getGroup("Exercise 2")
  part2 = exercise2.getGroup("Part 2")

  # This is equivalent to(but faster than):
  week1 = pf.getGroups("Week 1", full=True)
  exercise2 = week1[1]
  part2 = exercise2[1]
```


#### `submit(files)`
Submits the files to the exercise group. Default arguments are `judge=True`, `wait=True` and `silent=True`. `judge` will judge the submission instantly, and `wait` will wait for the submission to finish. Turning off `silent` will print the submission status dynamically.

```python
  suitcase[7].exercises[1].submit("suitcase.py", silent=False)

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



