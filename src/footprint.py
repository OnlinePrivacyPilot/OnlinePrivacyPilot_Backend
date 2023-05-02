from src import opp
from src import search
from src import scrap
from src import ftype
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from typing import Optional
import re

class Footprint(ABC):
    """
    This class is an abstract class that will define all the common attributes and method we want for our different type of footprint.

    Args:
        ABC (class): Here we are specifying that the class contains an abstract method.
    """
    _instances = []

    def __init__(self, fingerprint: opp, target: str, target_type: Optional[str] = None, method: Optional[str] = None):
        """
        Init function

        Args:
            fingerprint (opp.OPP): Fingerprint to which the footprint belongs
            target (str): Value of the footprint
            target_type (Optional[str], optional): Type of the  of the footprint. Defaults to None.
            method (Optional[str], optional): Method used to obtain footprint. Defaults to None.
        """
        Footprint._instances.append(self)
        self.belongs_to = fingerprint
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

class SearchableFootprint(Footprint):
    def __init__(self, fingerprint: opp, target: str, target_type: Optional[str] = None, method: Optional[str] = None, search_depth: int = 0, source_footprint: Optional[Footprint] = None, initial_filters: Optional[list] = []):
        super().__init__(fingerprint, target, target_type, method)
        self.source_footprint = source_footprint
        if self.source_footprint:
            self.search_depth = self.source_footprint.search_depth - 1 
        else:
            self.search_depth = search_depth
        self.initial_filters = initial_filters
        self.process()


    def process(self) -> None:
        search_obj = search.Search(filters=self.get_filters(), initial_filters=self.get_initial_filters())
        for item in search_obj.result:
            self.children_footprints.append(
                RecursionHandler.get(fingerprint=self.belongs_to, target=item["value"], source_footprint=self, method=item["method"], target_type=item["type"])
            )
    
    def get_filters(self) -> list:
        filters = []
        footprint = self

        # Add current Footprint as first filter
        filters.append(
            {
                "value" : footprint.target,
                "type" : footprint.target_type,
                "positive" : footprint.positive
            }
        )
        
        # If the current footprint is not a name or a username,
        # go back up the path in the treebelongs_to to retrieve the first name
        if footprint.target_type not in ["name", "username", "email", "phone"]:
            while footprint != None and footprint.target_type != "name":
                footprint = footprint.source_footprint
            if footprint and footprint.target_type == "name":
                filters.append(
                    {
                        "value" : footprint.target,
                        "type" : footprint.target_type,
                        "positive" : footprint.positive
                    }
                )
        return filters
    
    def get_initial_filters(self) -> list:
        footprint = self
        while footprint.source_footprint != None:
            footprint = footprint.source_footprint
        return footprint.initial_filters

class ScrapableFootprint(Footprint):
    def __init__(self, fingerprint: opp, target: str, target_type: Optional[str] = None, method: Optional[str] = None, source_footprint: Optional[Footprint] = None):
        super().__init__(fingerprint, target, target_type, method)
        self.source_footprint = source_footprint
        self.search_depth = self.source_footprint.search_depth - 1 
        self.process()
        
    def process(self) -> None:
        scrap_obj = scrap.Scrap(self.target).scrapper
        for item in scrap_obj.result:
            self.children_footprints.append(
                RecursionHandler.get(fingerprint=self.belongs_to, target=item["value"], source_footprint=self, method=item["method"], target_type=item["type"])
            )


class TerminalFootprint(Footprint):
    def __init__(self, fingerprint: opp, target: str, target_type: Optional[str] = None, method: Optional[str] = None, source_footprint: Optional[Footprint] = None):
        super().__init__(fingerprint, target, target_type, method)
        self.source_footprint = source_footprint
        self.process()

    def process(self) -> None:
        pass


class RecursionHandler:
    @classmethod
    def get(cls, fingerprint: opp, target: str, method: str, source_footprint: Footprint, target_type: Optional[str] = None) -> Footprint:
        if target_type == None:
            target_type = cls.eval_target_type(target)
        if source_footprint.search_depth > 0 and cls.check_target_not_duplicate(fingerprint, target):
            if target_type in ftype.SCRAPABLE_TYPES:
                return ScrapableFootprint(fingerprint=fingerprint, target=target, target_type=target_type, method=method, source_footprint=source_footprint)
            elif target_type in ftype.SEARCHABLE_TYPES:
                return SearchableFootprint(fingerprint=fingerprint, target=target, target_type=target_type, method=method, source_footprint=source_footprint)
        return TerminalFootprint(fingerprint=fingerprint, target=target, target_type=target_type, method=method, source_footprint=source_footprint)
    
    @classmethod
    def get_root(cls, fingerprint: opp, target: str = None, search_depth: int = 0, initial_filters: Optional[list] = []) -> Footprint:
            for i in range(len(initial_filters)):
                if not initial_filters[i]["type"]:
                    initial_filters[i]["type"] = cls.eval_target_type(initial_filters[i]["value"])
            return SearchableFootprint(fingerprint=fingerprint, target=target, target_type=cls.eval_target_type(target), method="user_input", search_depth=(search_depth - 1), initial_filters=initial_filters)
        
    @classmethod
    def eval_target_type(cls, target):
        if cls.is_url(target):
            return "url"
        elif cls.is_name(target):
            return "name"
        elif cls.is_username(target):
            return "username"
        elif cls.is_email(target):
            return "email"
        elif cls.is_phone(target):
            return "phone"
        else:
            return None
    
    @classmethod
    def check_target_not_duplicate(cls, belongs_to: opp, target: str) -> bool:
        for instance in Footprint.instances():
            if instance.belongs_to == belongs_to and instance.target.lower() == target.lower():
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
    
    def is_username(string: str) -> bool:
        username_regex = r'^[A-Za-z0-9_]+$'
        if re.fullmatch(username_regex, string):
            return True
        else:
            return False

    def is_email(string: str) -> bool:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,19}\b'
        if re.fullmatch(email_regex, string):
            return True
        else:
            return False
        
    def is_phone(string: str) -> bool:
        phone_regex = r'^\+?[0-9]{0,3}[0-9\ ]+$'
        if re.fullmatch(phone_regex, string):
            return True
        else:
            return False