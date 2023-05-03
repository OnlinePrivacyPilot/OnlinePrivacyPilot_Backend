from typing import Optional
from src import osint
from src import ftype
from googleapiclient.discovery import build
from jinja2 import Template
import requests
from bs4 import BeautifulSoup


class Search:
    def __init__(self, filters=None, initial_filters=None):
        self.filters = filters
        self.initial_filters = initial_filters
        self.query = ""
        self.result = []
        self.gen_results()

    def gen_results(self):
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

        """
            input: list of previous filters obtained in the path
            the main filter is always the last in the list
            all other elements of the list if exist are considered as positive filters
        """
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
    _instance = None

    def __new__(cls, api_key: str = None, cse_id: str =  None, active_search : bool = False):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.api_key = api_key
            cls.active_search = active_search
            cls.cse_id = cse_id
        return cls._instance