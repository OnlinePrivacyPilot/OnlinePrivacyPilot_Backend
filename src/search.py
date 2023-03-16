from src import credentials
from googleapiclient.discovery import build

class Search:
    def __init__(self, query=None, active_search=None):
        """
        Initialise un objet Search avec une requête et une option de recherche.

        Parameters
        ----------
        :param query: La requête de recherche à effectuer.
        :type query: str
        :param active_search: Si True, active également la recherche OSINT. Sinon, seulement la recherche Google est effectuée.
        :type active_search: bool
        :noindex:
        """
        self.query = query
        self.active_search = active_search
        self.result = []
        self.gen_results()

    def gen_results(self):
        """
        Generate results

        Parameters
        ----------
        :return: None
        :noindex:
        """
        self.mod_google()
        if self.active_search:
            self.mod_osint()
    
    def mod_google(self):
        """
        Modifies the search results by performing a Google search.

        Parameters
        ----------
        :return: None
        :noindex:
        """
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
        """
        Not implemented yet

        Parameters
        ----------
        :noindex:
        :return: None
        """
        return None
