from src import credentials
from googleapiclient.discovery import build
from itertools import permutations
from jinja2 import Environment, PackageLoader, Template

class Search:
    def __init__(self, filters=None, initial_filters=None):
        self.filters = filters
        self.initial_filters = initial_filters
        self.query = ""
        self.gen_results()

    def gen_results(self):
        self.prepare_query()

    def prepare_query(self) -> str:
        template = Template(
            "( {{ '\"' + p_0 | join('\" OR \"') + '\"' }} ){% if pos_filters | length > 0 %} AND ( {{ '\"' + pos_filters | join('\" OR \"', attribute='value') + '\"' }} ) {% endif %}{% if neg_filters | length > 0 %} {{ '-\"' + neg_filters | join('\" -\"', attribute='value') + '\"' }}{% endif %}"
        )

        p_i = []
        p_0 = []
        n_i = []

        MAIN_FILTERS_TYPE = ["name", "username"]
        SEARCHABLE_BUT_NOT_MAIN_TYPE = ["email", "location", "phone", "occupation"]
        OSINTABLE_TYPE = ["email", "phone"]

        for initf in self.initial_filters:
            if initf["positive"] == True:
                p_i.append(initf)
            else:
                n_i.append(initf)

        if self.filters[0]["type"] in SEARCHABLE_BUT_NOT_MAIN_TYPE:
            p_0_str = self.filters[len(self.filters)-1]["value"]
            for perm in self.get_permutations(p_0_str):
                p_0.append(perm)
            print(p_0)

            for filter in self.filters:
                if filter != p_0:
                    p_i.append(filter)

            if self.filters[0]["type"] in OSINTABLE_TYPE:
                self.mod_osint()

        elif self.filters[0]["type"] in MAIN_FILTERS_TYPE:
            p_0 = self.filters[0]
            i = 1
            while self.filters[i]["type"] not in MAIN_FILTERS_TYPE: #i <= len(self.filters) or
                p_i.append(self.filters[i])
                i += 1
        else:
            pass
        self.query = template.render(p_0=p_0, pos_filters=p_i, neg_filters=p_i)
    
    def mod_google(self):
        api_key = credentials.API_KEY
        search_engine_id = credentials.SEARCH_ENGINE_ID

        service = build("customsearch", "v1", developerKey=api_key)
        result = service.cse().list(q=self.query, cx=search_engine_id).execute()

        for item in result["items"]:
            self.result.append(
                {
                    "type" : "url",
                    "value" : item["link"],
                    "method" : "google"
                }
            )
    
    def mod_osint(self):
        return None
    
    def get_permutations(self,string=None):
        words = string.split()
        perms = permutations(words)
        perm_strings = [' '.join(perm) for perm in perms]
        return perm_strings
