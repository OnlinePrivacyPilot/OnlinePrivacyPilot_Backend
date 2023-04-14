from src import credentials
from googleapiclient.discovery import build
from itertools import permutations
from jinja2 import Template

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

        # Iterating on all the initial filters and appending them in the right list according to the value of their positive field
        for initf in self.initial_filters:
            (p_i if initf["positive"] == True else n_i).append(initf)

        """
            input: list of previous filters obtained in the path
            take the first element of the list
            if this is a filter searchable but not main, consider p_0 as the last element and iterate on the list while adding filters as positive ones
            elif if it is a main filter, consider p_0 again and iterate backwards, adding filters as positive ones until you find another main filter.
            else it is not a searchable filter and cannot be added as a filter.  
        """
        if self.filters[0]["type"] in SEARCHABLE_BUT_NOT_MAIN_TYPE:
            p_0 = [perm for perm in self.get_permutations(self.filters[-1]["value"])]
            p_i += [filter for filter in self.filters if filter != p_0 and filter["type"] in MAIN_FILTERS_TYPE + SEARCHABLE_BUT_NOT_MAIN_TYPE]
            # In addition, if OSINTABLE filter, call OSINT methods.
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
        self.query = template.render(p_0=p_0, pos_filters=p_i, neg_filters=n_i)
    
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
