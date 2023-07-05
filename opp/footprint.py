import hashlib
from opp import search
from opp import scrap
from opp import ftype
from abc import ABC, abstractmethod
from urllib.parse import urlparse
import re


class Footprint(ABC):
    """ This class is an abstract class that will define all the common attributes and method we want for our different types of footprint.

    Attributes:
        belongs_to (:class:`FingerprintHandler`): Fingerprint to which the footprint belongs
        target (str): Value of the footprint
        target_type (str, optional): Type of the  of the footprint. Defaults to None.
        method (str, optional): Method used to obtain footprint. Defaults to None.
    """
    _instances = []

    def __init__(self, fingerprint, target: str, target_type: str = None, method: str = None):
        Footprint._instances.append(self)
        self.belongs_to = fingerprint
        self.target = target
        self.target_type = target_type
        self.method = method
        self.positive = True
        self.children_footprints = []

    def instances() -> list:
        """ This method returns the list of all instances of :class:`Footprint`

        Returns:
            list: list of all instances of :class:`Footprint`
        """
        return Footprint._instances
    
    @abstractmethod
    def process(self) -> None:
        """ 
        This is an abstract method which is implemented in :class:`SearchableFootprint`, :class:`ScrapableFootprint` and :class:`TerminalFootprint` to manage investigations on all types of footprint. 
        
        """
        pass

class SearchableFootprint(Footprint):
    """ This class is inherited from Footprint, and is used to manage all types of footprint which be used to make queries to a search engine

    Attributes:
        belongs_to (:class:`FingerprintHandler`): inherited from Footprint
        target (str): inherited from Footprint
        target_type (str, optional): inherited from Footprint. Defaults to None.
        method (str, optional): inherited from Footprint. Defaults to None.
        search_depth (int, optional): Number of recursions remaining on the footprint. Defaults to 0.
        source_footprint (Footprint, optional): Footprint from which current one was obtained. Defaults to None.
        initial_filters (list, optional): Search filters given by the user. Defaults to [].
    """
    def __init__(self, fingerprint, target: str, target_type: str = None, method: str = None, search_depth: int = 0, source_footprint: Footprint = None, initial_filters: list = []):
        super().__init__(fingerprint, target, target_type, method)
        self.source_footprint = source_footprint
        if self.source_footprint:
            self.key = hash_string(str(self.source_footprint.key) + self.target)
            self.search_depth = self.source_footprint.search_depth - 1 
        else:
            self.key = hash_string(self.target)
            self.search_depth = search_depth
        self.initial_filters = initial_filters
        if self.initial_filters == []:
            self.initial_filters = self.get_initial_filters()
        self.process()


    def process(self) -> None:
        """
        This method instanciate :class:`Search <src.search.Search>` class, the results obtained are used to create new footprints objects by using :class:`RecursionHandler`

        """
        search_obj = search.Search(filters=self.get_filters(), initial_filters=self.initial_filters)
        for item in search_obj.result:
            if item["value"] not in [negative_filter["value"] for negative_filter in self.initial_filters if not negative_filter["positive"]]: # If not in initial negative filters
                self.children_footprints.append(
                    RecursionHandler.get(fingerprint=self.belongs_to, target=item["value"], source_footprint=self, method=item["method"], target_type=item["type"])
                )
    
    def get_filters(self) -> list:
        """ This method generates a list of filters which will be used to create a search query. It relies on the current footprint whose value is added directly to the list.
        If the current footprint is not a name or a username, go back up the path in the tree to retrieve the first footprint whose type is name.

        Returns:
            list: List of filters (1 or 2 elements), based on current footprint.
        """
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
        """ This method obtains the list of initial filters given by the user.

        Returns:
            list: List of initial filters.
        """
        footprint = self
        while footprint.source_footprint != None:
            footprint = footprint.source_footprint
        return footprint.initial_filters

class ScrapableFootprint(Footprint):
    """ This class is inherited from Footprint, and is used to manage all types of footprint which point to scrappable ressources

    Attributes:
        fingerprint (:class:`FingerprintHandler`): inherited from Footprint
        target (str): inherited from Footprint
        target_type (str, optional): inherited from Footprint. Defaults to None.
        method (str, optional): inherited from Footprint. Defaults to None.
        source_footprint (Footprint, optional): Footprint from which current one was obtained. Defaults to None.
    """
    def __init__(self, fingerprint, target: str, target_type: str = None, method: str = None, source_footprint: Footprint = None):

        super().__init__(fingerprint, target, target_type, method)
        self.source_footprint = source_footprint
        self.key = hash_string(str(self.source_footprint.key) + target)
        self.search_depth = self.source_footprint.search_depth - 1
        self.initial_filters = source_footprint.initial_filters
        self.process()
        
    def process(self) -> None:
        """
        This method instanciate :class:`Search <src.scrap.Scrap>` class, the results obtained are used to create new footprints objects by using :class:`RecursionHandler`

        """
        scrap_obj = scrap.Scrap(self.target).scrapper
        for item in scrap_obj.result:
            if item["value"] not in [negative_filter["value"] for negative_filter in self.initial_filters if not negative_filter["positive"]]: # If not in initial negative filters
                self.children_footprints.append(
                    RecursionHandler.get(fingerprint=self.belongs_to, target=item["value"], source_footprint=self, method=item["method"], target_type=item["type"])
                )


class TerminalFootprint(Footprint):
    """ This class is inherited from Footprint, and is used to manage all types of footprint that will not be used to obtain further information

    Attributes:
        fingerprint (:class:`FingerprintHandler`): inherited from Footprint
        target (str): inherited from Footprint
        target_type (str, optional): inherited from Footprint. Defaults to None.
        method (str, optional): inherited from Footprint. Defaults to None.
        source_footprint (Footprint, optional): Footprint from which current one was obtained. Defaults to None.
    """
    def __init__(self, fingerprint, target: str, target_type: str = None, method: str = None, source_footprint: Footprint = None):
        super().__init__(fingerprint, target, target_type, method)
        self.source_footprint = source_footprint
        self.key = hash_string(str(self.source_footprint.key) + target)
        self.process()

    def process(self) -> None:
        """
        This method does nothing because no further information is obtained from :class:`TerminalFootprint`

        """
        pass


class RecursionHandler:
    """
    This class is a toolbox to instanciate :class:`SearchableFootprint`, :class:`ScrapableFootprint` and :class:`TerminalFootprint` classes according the value of the given footprint.

    """
    @classmethod
    def get(cls, fingerprint, target: str, method: str, source_footprint: Footprint, target_type: str = None) -> Footprint:
        """ This method instanciates :class:`SearchableFootprint`, :class:`ScrapableFootprint` and :class:`TerminalFootprint` classes according the value of the given footprint.
        It allows to centralize the logic used to choose the right class for each footprint according its type.

        Args:
            fingerprint (:class:`FingerprintHandler`): Fingerprint to which the footprint belongs
            target (str): Value of the footprint
            method (str): Method used to obtain footprint
            source_footprint (Footprint): _description_
            target_type (str, optional): Type of the  of the footprint. Defaults to None.
        Returns:
            Footprint: An object :class:`SearchableFootprint`, :class:`ScrapableFootprint` or :class:`TerminalFootprint` correctly instanciated.
        """
        if target_type == None:
            target_type = cls.eval_target_type(target)
        if source_footprint.search_depth > 0 and cls.check_target_not_duplicate(fingerprint, target):
            if target_type in ftype.SCRAPABLE_TYPES:
                return ScrapableFootprint(fingerprint=fingerprint, target=target, target_type=target_type, method=method, source_footprint=source_footprint)
            elif target_type in ftype.SEARCHABLE_TYPES:
                return SearchableFootprint(fingerprint=fingerprint, target=target, target_type=target_type, method=method, source_footprint=source_footprint)
        return TerminalFootprint(fingerprint=fingerprint, target=target, target_type=target_type, method=method, source_footprint=source_footprint)
    
    @classmethod
    def get_root(cls, fingerprint, target: str, search_depth: int = 0, initial_filters: list = []) -> Footprint:
        """ This method instanciates :class:`SearchableFootprint` class for the first footprint of the tree.

        Args:
            fingerprint (:class:`FingerprintHandler`): Fingerprint to which the footprint belongs.
            target (str): Value of the footprint.
            search_depth (int, optional): Number of recursions remaining on the footprint. Defaults to 0.
            initial_filters (list, optional): Search filters given by the user. Defaults to [].

        Returns:
            Footprint: An object :class:`SearchableFootprint` correctly instanciated.
        """
        for i in range(len(initial_filters)):
            if not initial_filters[i]["type"]:
                initial_filters[i]["type"] = cls.eval_target_type(initial_filters[i]["value"])
        return SearchableFootprint(fingerprint=fingerprint, target=target, target_type=cls.eval_target_type(target), method="user_input", search_depth=(search_depth - 1), initial_filters=initial_filters)
        
    @classmethod
    def eval_target_type(cls, target: str) -> str:
        """ This method evaluate the target to determine its type.

        Args:
            target (str): Value of the target to evaluate.

        Returns:
            str: Type of the given target.
        """
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
    def check_target_not_duplicate(cls, belongs_to, target: str) -> bool:
        """ This method checks if target footprint already exists in the tree, if yes no new recursion will be done on it.

        Args:
            belongs_to (:class:`FingerprintHandler`): Fingerprint tree to which the check must be limited
            target (str): Value of the target footprint to check.

        Returns:
            bool: Existence of the target footprint.
        """
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
        
def hash_string(string: str):
    encoded_string = string.encode('utf-8')
    hash_object = hashlib.sha256(encoded_string)
    hex_dig = hash_object.hexdigest()
    return hex_dig