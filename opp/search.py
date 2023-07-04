from typing import Optional
from opp import osint
from opp import ftype
from googleapiclient.discovery import build
from jinja2 import Template
import requests
from bs4 import BeautifulSoup


class Search:
    """ This class is instanciated with filters from the tree and initial filters given by the user. 

    Attributes:
        filters (list, optional): Filters from the tree. Defaults to [].
        initial_filters (list, optional): Initial filters given by the user. Defaults to [].
        query (str): Query prepared according the filters.
        result (list): List of obtained footprints.
    
    Example:
        Here is the example list of filters to show the structure :

        >>> filters = [
        ...     {
        ...         "value" : "Paris",
        ...         "type" : "location",
        ...         "positive" : True
        ...     },
        ...     {
        ...         "value" : "Paul Martin",
        ...         "type" : "name",
        ...         "positive" : True
        ...     }
        ... ]

    """
    def __init__(self, filters: list = [], initial_filters: list = []):
        self.filters = filters
        self.initial_filters = initial_filters
        self.query = ""
        self.result = []
        self.gen_results()

    def gen_results(self):
        """ This method calls `prepare_query()` to obtain query,
        then according the options in :class:`SearchOptions` it calls a search engine method
        (`mod_google()` or `mod_google_no_api`),
        finally according the type of the first filter and if OSINT investigations are activated
        in :class:`SearchOptions`, it calls the right function in osint module.

        All obtained footprints are added to `result` attribute of the current :class:`Search` object.
        """
        self.prepare_query()
        if SearchOptions().api_key and SearchOptions().cse_id:
            self.mod_google()
        else:
            self.mod_google_no_api()

        # In addition, if OSINTABLE filter, call OSINT methods.
        if len(self.filters) != 0 and SearchOptions.active_search == True:
            if self.filters[0]["type"] == "email":
                self.result += osint.email(self.filters[0]["value"])
            elif self.filters[0]["type"] == "phone":
                self.result += osint.phone(self.filters[0]["value"])


    def prepare_query(self) -> str:
        """ This method prepares a query according the filters instanciated in the current :class:`Search` object.
            
            Here is the strategy : 
            
            `filters` are obtained in the current path of the tree, the main filter is always the last of this list,
            all other elements of the list if exist are considered as positive filters.

            `initial_filters` are simply concatenated to positive and negative filters according the value their attribute "positive". 
        Returns:
            str: _description_
        """
        QUERY_TEMPLATE = Template(
            "( {{ '\"' + p_0 | join('\" OR \"') + '\"' }} ){% if pos_filters | length > 0 %} AND ( {{ '\"' + pos_filters | join('\" OR \"', attribute='value') + '\"' }} ) {% endif %}{% if neg_filters | length > 0 %} {{ '-\"' + neg_filters | join('\" -\"', attribute='value') + '\"' }}{% endif %}"
        )

        p_i = []
        p_0 = []
        n_i = []

        # Iterating on all the initial filters and appending them in the right list according to the value of their positive field
        for initf in self.initial_filters:
            if initf["positive"]:
                p_i.append(initf)
            else:
                n_i.append(initf)

        if len(self.filters) != 0:
            p_0 = [self.filters[-1]["value"]]
            p_i += [filter for filter in self.filters[:-1] if filter["type"] in ftype.SEARCHABLE_TYPES]
        # Generating query
        self.query = QUERY_TEMPLATE.render(p_0=p_0, pos_filters=p_i, neg_filters=n_i)
    
    def mod_google(self):
        api_key = SearchOptions.api_key
        search_engine_id = SearchOptions.cse_id

        number_of_page = 3
        start = 1
        result = {}
        #Result per page is apparently set to 10 by default

        while start < number_of_page*10:
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=self.query, cx=search_engine_id, start=start).execute()
            if "items" in result:
                for item in result["items"]:
                    self.result.append(
                        {
                            "type" : "url",
                            "value" : item["link"],
                            "method" : "google"
                        }
                    )
            start += 10
                   
    def mod_google_no_api(self):
        url = 'https://www.google.com/search?nfpr=1&q='+ self.query.replace(" ", "+")
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0'}
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='g')
        for result in results:
            try:
                self.result.append(
                    {
                        "type" : "url",
                        "value" : result.find('a')['href'],
                        "method" : "google"
                    }
                )
            except KeyError:
                pass

class SearchOptions:
    """ This singleton class allows to store search options : Google API key, Google CSE ID and Active search.

    Attributes:
        api_key (str, optional): Google API key. Defaults to None.
        cse_id (str, optional): Google CSE ID. Defaults to None.
        active_search (bool, optional): This option activates OSINT investigations. Defaults to False.
    """
    _instance = None

    def __new__(cls, api_key: str = None, cse_id: str =  '566c87e9879ac4d59', active_search : bool = False):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.api_key = api_key
            cls.active_search = active_search
            cls.cse_id = cse_id
        return cls._instance