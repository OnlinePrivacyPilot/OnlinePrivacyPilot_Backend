from src import footprint
from src import storage
from typing import Optional

class OPP:
    def __init__(self, target: str = None, target_type: Optional[str] = None, search_depth: Optional[int] = 3, initial_filters: list = None):
        self.target = target
        self.target_type = target_type
        self.search_depth = search_depth
        self.storage = storage.Storage(target.replace(' ', '_')+".db")
        self.fingerprint = footprint.RecursionHandler.get_root(target=self.target, search_depth=search_depth, initial_filters=initial_filters)


    def get_fingerprint(self):
        return self.fingerprint

