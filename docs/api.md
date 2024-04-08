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
assignments = pf.getExerciseGroups()
```

### Methods
#### `getExerciseGroups()`
Returns a list of `ExerciseGroup` instances corresponding to all exercise groups visible to the user in a given `Course`.

```python
assignments = pf.getExerciseGroups()
```

## `ExerciseGroup`
When this class is initialized, it will automatically fetch the exercise's info, files and test cases(it might be slow, because it indexes the entire course, which I will fix at some point).

* Both folders and exercises are represented as `ExerciseGroup` instances.
* Folders will have the `amExercise` attribute set to `False`.
* Folders can have the `downloadFiles` method called on them.
* Exercises can have the `submit`, `downloadFiles` and `downloadTCs` method called on them.


### Usage
```python
pf = year.getCourse("Programming Fundamentals (for CS)")
assignments = pf.getExerciseGroups()
assignment = assignments[0]
print(assignment.amExercise) # <- Exercise or folder attribute
print(assignment.files) # <- Downloadable files attribute
print(assignment.testCases) # <- Test cases attribute

print(assignment.folders) # <- If the group contains folders, they will be here
print(assignment.exercises) # <- If the group contains exercises, they will be here
```

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
week1 = assignments[0].folders[0]
exercise2 = week1.exercises[1]
part2 = exercise2.folders[1]
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


