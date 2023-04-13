from src import search
from src import scrap
from src import storage
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from typing import Optional

class Footprint(ABC):
    """
    This class is an abstract class that will define all the common attributes and method we want for our different type of footprint.

    Args:
        ABC (class): Here we are specifying that the class contains an abstract method.
    """
    _instances = []

    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None):
        """
        Init function

        Args:
            target (str, optional): The input of the user we are the investigated in. Defaults to None.
            target_type (Optional[str], optional): Type of the target is we know it so far. Defaults to None.
            method (Optional[str], optional): The way we used to obtain this footprint. Defaults to None.
            search_depth (int, optional): The user has also the choice of teh depth of the recursion while we are scraping. Defaults to 0.
            source_footprint_id (int, optional): Storage of the parent id the footprint is coming from. Defaults to None.
        """
        Footprint._instances.append(self)
        self.target = target
        self.target_type = target_type
        self.method = method
        self.positive = True
        self.children_footprints = []

    def instances():
        return Footprint._instances
    
    @abstractmethod
    def process(self) -> None:
        pass
    
    def store_fp(self, source_footprint_id: int = None) -> int:
        """
        This function is responsible of the storage of our footprint.
        It will create a node in the database and the edges associated with it. 

        :param source_footprint_id: with this attribute we are able to keep the id of the footprint above the current footprint in the tree. 
            Used to build edges. Defaults to None.
        :type source_footprint_id: int, optional

        :returns: the id of the footprint
        """
        footprint_id = storage.Storage().store_node(self.method, self.target_type, self.target)
        if source_footprint_id:
            storage.Storage().store_edge(source_footprint_id, footprint_id)
        return footprint_id
            

class SearchableFootprint(Footprint):
    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, search_depth: int = 0, source_footprint: Optional[Footprint] = None, initial_filters: Optional[list] = []):
        super().__init__(target, target_type, method)
        self.source_footprint = source_footprint
        if self.source_footprint:
            self.search_depth = self.source_footprint.search_depth - 1 
            self.id = self.store_fp(self.source_footprint.id)
        else:
            self.search_depth = search_depth
            self.id = self.store_fp(None)
        self.initial_filters = initial_filters
        self.process()


    def process(self) -> None:
        search_obj = search.Search(filters=self.get_filters(), initial_filters=self.get_initial_filters())
        for item in search_obj.result:
            self.children_footprints.append(
                RecursionHandler.get(target=item["value"], source_footprint=self, method=item["method"], target_type=item["type"])
            )
    
    def get_filters(self) -> list:
        filters = []
        footprint = self
        while footprint != None:
            if isinstance(footprint, SearchableFootprint):
                filters.append(
                    {
                        "value" : footprint.target,
                        "type" : footprint.target_type,
                        "positive" : footprint.positive
                    }
                )
            footprint = footprint.source_footprint
        return filters
    
    def get_initial_filters(self) -> list:
        footprint = self
        while footprint.source_footprint != None:
            footprint = footprint.source_footprint
        return footprint.initial_filters

class ScrapableFootprint(Footprint):
    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, source_footprint: Optional[Footprint] = None):
        super().__init__(target, target_type, method)
        self.source_footprint = source_footprint
        self.search_depth = self.source_footprint.search_depth - 1 
        self.id = self.store_fp(self.source_footprint.id)
        self.process()
        
    def process(self) -> None:
        scrap_obj = scrap.Scrap(self.target).scrapper
        for item in scrap_obj.result:
            self.children_footprints.append(
                RecursionHandler.get(target=item["value"], source_footprint=self, method=item["method"], target_type=item["type"])
            )


class TerminalFootprint(Footprint):
    def __init__(self, target: str = None, target_type: Optional[str] = None, method: Optional[str] = None, source_footprint: Optional[Footprint] = None):
        super().__init__(target, target_type, method)
        self.source_footprint = source_footprint
        if self.source_footprint:
            self.id = self.store_fp(self.source_footprint.id)
        else:
            self.id = self.store_fp(None)
        self.process()

    def process(self) -> None:
        pass


class RecursionHandler:
    SCRAPABLE_TYPES = ["url"]
    #SEARCHABLE_TYPES = ["name", "location", "email", "username", "phone", "occupation"]
    SEARCHABLE_TYPES = ["name"]

    @classmethod
    def get(cls, target: str, method: str, source_footprint: Footprint, target_type: Optional[str] = None) -> Footprint:
        if target_type == None:
            target_type = cls.eval_target_type(target)
        if source_footprint.search_depth > 0 and cls.check_target_not_duplicate(target):
            if target_type in cls.SCRAPABLE_TYPES:
                return ScrapableFootprint(target=target, target_type=target_type, method=method, source_footprint=source_footprint)
            elif target_type in cls.SEARCHABLE_TYPES:
                return SearchableFootprint(target=target, target_type=target_type, method=method, source_footprint=source_footprint)
        return TerminalFootprint(target=target, target_type=target_type, method=method, source_footprint=source_footprint)
    
    @classmethod
    def get_root(cls, target: str = None, search_depth: int = 0, initial_filters: Optional[list] = []) -> Footprint:
            return SearchableFootprint(target=target, target_type=cls.eval_target_type(target), method="user_input", search_depth=(search_depth - 1), initial_filters=initial_filters)
        
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
    
    @classmethod
    def check_target_not_duplicate(cls, target: str) -> bool:
        for instance in Footprint.instances():
            if instance.target.lower() == target.lower():
                return False
        return True


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
