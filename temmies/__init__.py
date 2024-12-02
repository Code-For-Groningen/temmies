"""
Entry point for the temmies package.
"""
import urllib3
from .themis import Themis

__all__ = ["Themis"]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
