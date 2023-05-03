from src import footprint
from typing import Optional
from collections import OrderedDict

class FingerprintHandler:
    def __init__(self, target: str = None, target_type: str = None, search_depth: int = 3, initial_filters: list = []):
        self.target = target
        self.target_type = target_type
        self.search_depth = search_depth
        self.initial_filters = initial_filters

    def get_fingerprint(self):
        return footprint.RecursionHandler.get_root(fingerprint=self, target=self.target, search_depth=self.search_depth, initial_filters=self.initial_filters)

    def get_ascii_tree(self, fp: footprint.Footprint):
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

    def get_json_tree(self, fp: footprint.Footprint):
        if isinstance(fp, footprint.Footprint):
            if fp.children_footprints:
                if fp.source_footprint:
                    return [{
                                "value": child_fp.target.replace('\n', ' '),
                                "type": child_fp.target_type,
                                "method": child_fp.method,
                                "child": self.get_json_tree(child_fp)
                            } for child_fp in fp.children_footprints ]
                else:
                    return {
                                "value": fp.target.replace('\n', ' '),
                                "type": fp.target_type,
                                "method": fp.method,
                                "child": [{
                                            "value": child_fp.target.replace('\n', ' '),
                                            "type": child_fp.target_type,
                                            "method": child_fp.method,
                                            "child": self.get_json_tree(child_fp)
                                        } for child_fp in fp.children_footprints ]
                            }
            else:
                if fp.source_footprint:
                    return {}
                else: 
                    return {
                                "value": fp.target.replace('\n', ' '),
                                "type": fp.target_type,
                                "method": fp.method,
                                "child": []
                            }