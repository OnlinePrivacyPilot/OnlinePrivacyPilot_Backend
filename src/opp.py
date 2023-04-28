from src import footprint
from src import storage
from typing import Optional
from collections import OrderedDict

class OPP:
    def __init__(self, target: str = None, target_type: Optional[str] = None, search_depth: Optional[int] = 3, initial_filters: list = []):
        self.target = target
        self.target_type = target_type
        self.search_depth = search_depth
        self.fingerprint = footprint.RecursionHandler.get_root(target=self.target, search_depth=search_depth, initial_filters=initial_filters)


    def get_fingerprint(self):
        return self.fingerprint

    def get_ascii_tree(self, fp: footprint):
        if isinstance(fp, footprint.Footprint):
            if fp.children_footprints:
                if fp.source_footprint:
                    return OrderedDict([(f"%s (type: %s, method: %s)" % (child_fp.target.replace('\n', ' '), child_fp.target_type, child_fp.method), self.get_ascii_tree(child_fp) ) for child_fp in fp.children_footprints])
                else:
                    return {f"%s (type: %s, method: %s)" % (fp.target.replace('\n', ' '), fp.target_type, fp.method): OrderedDict([(f"%s (type: %s, method: %s)" % (child_fp.target.replace('\n', ' '), child_fp.target_type, child_fp.method), self.get_ascii_tree(child_fp) ) for child_fp in fp.children_footprints])}
            else:
                if fp.source_footprint:
                    return {}
                else: 
                    return {f"%s (type: %s, method: %s)" % (fp.target.replace('\n', ' '), fp.target_type, fp.method): {}}
