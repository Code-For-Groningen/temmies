"""
Illegal Action Exception 
"""

class IllegalAction(Exception):
    """Illegal Action Exception"""
    def __init__(self, message: str = ""):
        super().__init__(f"Illegal action: {message}")
