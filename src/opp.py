from src import footprint
from src import storage
from typing import Optional

class OPP:
    def __init__(self, target: str = None, target_type: Optional[str] = None, search_mode: Optional[str] = None, search_depth: int = 3):
        self.target = target
        self.target_type = target_type
        self.search_mode = search_mode if search_mode else False
        self.search_depth = search_depth
        self.storage = storage.Storage(target.replace(' ', '_')+".db")
        self.fingerprint = footprint.RecursionHandler.get(self.target, self.target_type, "user_input", self.search_mode, search_depth)

    def get_fingerprint(self):
        return self.fingerprint

