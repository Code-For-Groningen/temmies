from .group import Group


class Course(Group):
    """
    Represents a course.
    """

    def __init__(self, session, course_path: str, title: str, parent):
        super().__init__(session, course_path, title, parent)
        self.course_path = course_path  # e.g., '/2023-2024/adinc-ai'

    def __str__(self):
        return f"Course({self.title})"

    def create_group(self, item_data):
        """
        Create a subgroup (Group or ExerciseGroup) based on item data.
        """
        if item_data.get("submitable", False):
            return ExerciseGroup(
                self.session,
                item_data["path"],
                item_data["title"],
                self,
                item_data.get("submitable", False),
            )
        else:
            return Group(
                self.session,
                item_data["path"],
                item_data["title"],
                self,
                item_data.get("submitable", False),
            )
