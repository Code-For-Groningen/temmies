
## **Changelog**

### **Version 1.1.0**

#### **Documentation**
- Fixed method signatures to align with actual functionality.
- Updated `get_status` to properly handle `Submission` instances.
- Ensured all class and method examples are consistent with the codebase.

#### **Codebase**
- Prepended `get_` to all methods in `Submission`
- Created base `Group` from which `Course` and `ExerciseGroup` inherit.
- Using system keyring to store passwords (Issue #11)

### **Version 1.2.0**

#### **Codebase**
- Moved all methods related to downloading files (including test cases) to `Group`.
- Created `get_test_cases` and `get_files` methods in `Group`.
- We are now using the [API](https://themis.housing.rug.nl/api/navigation/2023-2024) (which mysteriously appeared) to get the year/course structure.