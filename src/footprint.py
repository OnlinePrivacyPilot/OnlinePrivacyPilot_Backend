from src import search
from src import scrap
from src import storage
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from typing import Optional

class Footprint(ABC):
    """
    A simple docstring.

    """
    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, active_search: Optional[str] = None, search_depth: int = 0, source_footprint_id: int = None):
        self.target = target
        self.target_type = target_type
        self.method = method
        self.active_search = active_search
        self.search_depth = search_depth
    
    @abstractmethod
    def process(self) -> None:
        pass
    
    def store_fp(self, source_footprint_id: int = None) -> int:
        footprint_id = storage.Storage().store_node(self.method, self.target_type, self.target)
        if source_footprint_id:
            storage.Storage().store_edge(source_footprint_id, footprint_id)
        return footprint_id
            

class SearchableFootprint(Footprint):
    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, active_search: Optional[str] = None, search_depth: int = 0, source_footprint_id: int = None):
        super().__init__(target, target_type, method, active_search, search_depth, source_footprint_id)
        self.footprint_id = self.store_fp(source_footprint_id)
        self.process()


    def process(self) -> None:
        search_obj = search.Search(self.target, self.active_search)
        children_footprints = []
        for item in search_obj.result:
            children_footprints.append(
                RecursionHandler.get(item["value"], item["type"], item["method"], self.active_search, self.search_depth, self.footprint_id)
            )

class ScrapableFootprint(Footprint):
    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, active_search: Optional[str] = None, search_depth: int = 0, source_footprint_id: int = None):
        super().__init__(target, target_type, method, active_search, search_depth, source_footprint_id)
        self.footprint_id = self.store_fp(source_footprint_id)
        self.process()

    def process(self) -> None:
        scrap_obj = scrap.Scrap(self.target).scrapper
        children_footprints = []
        for item in scrap_obj.result:
            children_footprints.append(
                RecursionHandler.get(item["value"], item["type"], item["method"], self.active_search, self.search_depth, self.footprint_id)
            )


class TerminalFootprint(Footprint):
    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, active_search: Optional[str] = None, source_footprint_id: int = None):
        super().__init__(target, target_type, method, active_search, source_footprint_id)
        self.footprint_id = self.store_fp(source_footprint_id)
        self.process()
    
    def process(self) -> None:
        pass


class RecursionHandler:
    SCRAPABLE_TYPES = ["url"]
    SEARCHABLE_TYPES = ["name"]

    @classmethod
    def get(cls, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, active_search: Optional[str] = None, search_depth: Optional[int] = 0, source_footprint_id: int = None) -> Footprint:
        if target_type == None:
            target_type = cls.eval_target_type(target)
        if search_depth > 0:
            if target_type in cls.SCRAPABLE_TYPES:
                return ScrapableFootprint(target, target_type, method, active_search, (search_depth - 1), source_footprint_id)
            elif target_type in cls.SEARCHABLE_TYPES:
                return SearchableFootprint(target, target_type, method, active_search, (search_depth - 1), source_footprint_id)
        return TerminalFootprint(target, target_type, method, active_search, source_footprint_id)

    @classmethod
    def eval_target_type(cls, target):
        # URL ?
        if cls.is_url(target):
            return "url"
        # Name ?
        elif cls.is_name(target):
            return "name"
        else:
            return None

    def is_url(string: str) -> bool:
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def is_name(string: str) -> bool:
        for word in str(string).split(" "):
            if not " ".join(word.split()).isalpha():
                return False
        return True
