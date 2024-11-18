from .themis import Themis
import urllib3

__all__ = ["Themis"]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
