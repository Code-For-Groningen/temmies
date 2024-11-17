
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