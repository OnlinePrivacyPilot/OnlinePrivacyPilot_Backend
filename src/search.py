import json
from typing import Optional
from src import credentials
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
        if SearchOptions.api_key != "":
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
            take the first element of the list
            if this is a filter searchable but not main, consider p_0 as the last element and iterate on the list while adding filters as positive ones
            elif if it is a main filter, consider p_0 again and iterate backwards, adding filters as positive ones until you find another main filter.
            else it is not a searchable filter and cannot be added as a filter.  
        """
        if len(self.filters) != 0:
            if self.filters[0]["type"] in ftype.MAIN_FILTERS:
                p_0 = [self.filters[0]["value"]]
            elif self.filters[0]["type"] in ftype.FILTERS:
                p_0 = [self.filters[-1]["value"]]
                p_i += [filter for filter in self.filters[:-1] if filter["type"] in ftype.SEARCHABLE_TYPES]
        # Generating query
        self.query = QUERY_TEMPLATE.render(p_0=p_0, pos_filters=p_i, neg_filters=n_i)
    
    def mod_google(self):
        api_key = SearchOptions.api_key
        search_engine_id = credentials.SEARCH_ENGINE_ID

        service = build("customsearch", "v1", developerKey=api_key)
        result = service.cse().list(q=self.query, cx=search_engine_id).execute()

        if "items" in result:
            for item in result["items"]:
                self.result.append(
                    {
                        "type" : "url",
                        "value" : item["link"],
                        "method" : "google"
                    }
                )

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

    """
    if API key in config file, then we will consider it.
        if the config file gives a wrong API it will be handdle by google
        if there is also an input we will consider the config file and notify the user
    if no API key and no config file we will create one and append the input
    if no API key and no input we will apply scrapping techniques
    if empty key in the config file we will scrap
    """

    def __new__(cls, api_key : Optional[str]="", active_search : Optional[bool]=False):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.api_key = api_key
            cls.active_search = active_search
            cls.config_file = "config.json"
            cls.load_config(cls)
        return cls._instance

    def load_config(cls):
        try:
            with open(cls.config_file, "r") as f:
                config = json.load(f)
                init_api_key = cls.api_key
                cls.api_key = config.get("api_key", cls.api_key)
                #If we found both an API key in the config file and as an input we take the one from the config file
                if cls.api_key != "" and init_api_key:
                    raise ValueError("API key found in your configuration file, but also as an input, the one from " + cls.config_file + " will be considered")
        except (FileNotFoundError):
            config = {
            "api_key": cls.api_key,
            }

            with open(cls.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except (ValueError) as e:
            print(e)
