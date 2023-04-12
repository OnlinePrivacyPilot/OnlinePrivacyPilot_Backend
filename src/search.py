from src import credentials
from googleapiclient.discovery import build

class Search:
    def __init__(self, query=None, active_search=None):
        self.query = query
        self.active_search = active_search
        self.result = []
        self.gen_results()

    def gen_results(self):
        self.mod_google()
        if self.active_search:
            self.mod_osint()
    
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
