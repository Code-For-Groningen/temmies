""" This module contains the CourseUnavailable exception. """

class CourseUnavailable(Exception):
    """CourseUnavailable Exception"""
    def __init__(self, message: str = ""):
        super().__init__(f"Course unavailable: {message}")
