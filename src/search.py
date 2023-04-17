from src import credentials
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
        self.mod_google()

        # In addition, if OSINTABLE filter, call OSINT methods.
        if len(self.filters) != 0 and self.filters[0]["type"] in ["email", "phone"]:
            self.mod_osint()

    def prepare_query(self) -> str:
        MAIN_FILTERS_TYPE = ["name", "username"]
        SEARCHABLE_BUT_NOT_MAIN_TYPE = ["email", "location", "phone", "occupation"]
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
            if self.filters[0]["type"] in MAIN_FILTERS_TYPE:
                p_0 = [self.filters[0]]
            elif self.filters[0]["type"] in SEARCHABLE_BUT_NOT_MAIN_TYPE:
                p_0 = [self.filters[-1]]
                p_i += [filter for filter in self.filters[:-1] if filter["type"] in MAIN_FILTERS_TYPE + SEARCHABLE_BUT_NOT_MAIN_TYPE]
        # Generating query
        self.query = QUERY_TEMPLATE.render(p_0=p_0, pos_filters=p_i, neg_filters=n_i)
    
    def mod_google(self):
        api_key = credentials.API_KEY
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
        url = 'https://www.google.com/search?q='+ self.query.replace(" ", "+")
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

    
    def mod_osint(self):
        pass

