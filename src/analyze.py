import urllib.request
import spacy
from bs4 import BeautifulSoup

class Analyze:
    def __init__(self, data=None, res=None):
        self.data = data
        self.res = res

    def set_data(self, data):
        self.data = data

    def set_res(self, res):
        self.res = res

    def extract_nlp(self):
        nlp = spacy.load("en_core_web_sm")

        for url in self.data:
            text = ""

            if url.find('&rut') != -1:
                url = url[:url.find('&rut')]

            try :
                html = urllib.request.urlopen(url).read()
            except :
                print("No answer from the link: ", url)
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            doc = nlp(text.replace("\n", " "))
            for entity in doc.ents:
                self.res.append({entity.text, entity.label_})

        return self.res
            
        
        
        
