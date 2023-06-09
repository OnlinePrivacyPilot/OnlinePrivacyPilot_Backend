from urllib.parse import urlparse
from opp import footprint
from typing import Optional
from collections import OrderedDict

class FingerprintHandler:
    def __init__(self, target: str = None, target_type: str = None, search_depth: int = 3, initial_filters: list = []):
        self.target = target
        self.target_type = target_type
        self.search_depth = search_depth
        self.initial_filters = initial_filters

    def get_fingerprint(self) -> footprint.Footprint:
        """ This method calls :class:`footprint.RecursionHandler` class to build recursively the fingerprint tree.

        Returns:
            Footprint: Root footprint of the obtained fingerprint
        """
        return footprint.RecursionHandler.get_root(fingerprint=self, target=self.target, search_depth=self.search_depth, initial_filters=self.initial_filters)

    def get_ascii_tree(self, fp: footprint.Footprint) -> dict:
        """ This method returns a dictionnary that can be used by asciitree module to display the fingerprint tree in the terminal.

        Args:
            fp (footprint.Footprint): Fingerprint to display.

        Returns:
            dict: asciitree compatible dict
        """
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

    def get_json_tree(self, fp: footprint.Footprint) -> dict:
        """ This method returns a dictionnary used in order to make JSON response in the REST API.

        Args:
            fp (footprint.Footprint): Fingerprint to display.

        Returns:
            dict: JSON compatible dict
        """
        if isinstance(fp, footprint.Footprint):
            if fp.children_footprints:
                if fp.source_footprint:
                    return [{
                                "key": child_fp.key,
                                "value": child_fp.target.replace('\n', ' '),
                                "type": child_fp.target_type,
                                "method": child_fp.method,
                                "child": self.get_json_tree(child_fp)
                            } for child_fp in fp.children_footprints ]
                else:
                    return {
                                "key": fp.key,
                                "value": fp.target.replace('\n', ' '),
                                "type": fp.target_type,
                                "method": fp.method,
                                "child": [{
                                            "key": child_fp.key,
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
                                "key": fp.key,
                                "value": fp.target.replace('\n', ' '),
                                "type": fp.target_type,
                                "method": fp.method,
                                "child": []
                            }

    def get_json_nodes_edges(self, fp: footprint.Footprint):
        result = {
            "nodes": [],
            "edges": []
        }
        edge_key = -1
        def traverse(fp):
            nonlocal edge_key
            edge_key += 1
            current_key = fp.key
            fp_data = {
                "key": current_key,
                "attributes": {
                    "label":  self.prettify_link(fp.target.replace('\n', ' ')) if fp.target_type == 'url' else fp.target.replace('\n', ' '),
                    "target": fp.target.replace('\n', ' '),
                    "target_type": fp.target_type,
                    "method": fp.method
                }
            }
            result["nodes"].append(fp_data)
            if fp.children_footprints:
                for child_fp in fp.children_footprints:
                    edge_data = {
                        "key": edge_key,
                        "source": current_key,
                        "target": traverse(child_fp),
                        "attributes": {}
                    }
                    result["edges"].append(edge_data)
            return current_key
        traverse(fp)
        return result

    def prettify_link(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")
        path = parsed_url.path.strip('/')

        if domain:
            display_text = f"{domain}: {path}" if path else domain
        else:
            display_text = url 

        return display_text
