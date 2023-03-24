import urllib.request
import spacy
from bs4 import BeautifulSoup
from typing import List
from spacy.matcher import Matcher
from spacy.language import Language
from spacy.tokens import Span


'''
doc.ents is an attribute of the Doc object that contains a sequence of Span objects representing the named entities identified by the ner component during the processing of the Doc. doc.ents is read-only, meaning that you cannot modify or add to it directly.

On the other hand, Span objects are created and modified programmatically by the user or custom pipeline components, using methods such as doc[start:end], doc.char_span(), or by merging or splitting existing Span objects. Span objects can be assigned custom labels, merged with other Span objects, or updated with additional information beyond the label and text.
'''

'''
In spaCy, a Span object represents a contiguous sequence of tokens within a Doc. It is defined by its starting and ending token indices within the Doc. The Span object provides various attributes and methods to access or modify its text, label, and other properties. It is a fundamental object in spaCy for working with entities, phrases, and other sub-parts of text data.
'''


class Analyze:
  
    @classmethod
    def extract_nlp(cls, data: str = None) -> List:
        result = []

        nlp = spacy.load("en_core_web_md")

        nlp.add_pipe("usernames_ner", before="ner")
        nlp.add_pipe("emails_ner")
        nlp.add_pipe("remove_gpe")
        doc = nlp(data)
        
        #print(nlp.analyze_pipes())

        for entity in doc.ents:
            result.append([entity.text, entity.label_])

        return result
    
    @Language.component("usernames_ner", assigns=["token.ORTH", "token.TAG"])
    def identify_usernames(doc):
        username_pattern = [{"ORTH": "@"}, {"IS_ALPHA": True}]
        matcher = Matcher(doc.vocab)
        matcher.add("USERNAME", [username_pattern])
        matches = matcher(doc)
        spans = []
        for start, end in matches:
            span = doc[start:end]
            spans.append(span)
        for span in spans:
            span.merge(tag="USERNAME", lemma=span.text)
        return doc
    
    @Language.component("emails_ner")
    def identify_emails(doc):
        matcher = Matcher(doc.vocab)
        pattern = [{'TEXT': {'REGEX': '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'}}]
        matcher.add('EMAIL_ADDRESS', [pattern])
        matches = matcher(doc)
        spans = []
        for start, end in matches:
            span = doc[start:end]
            spans.append(span)
        for span in spans:
            email_ent = Span(doc, span.start, span.end, label="EMAIL_ADDRESS")
            doc.ents = list(doc.ents) + [email_ent]
        return doc
    
    @Language.component("phone_numbers_ner")
    def identify_phone_numbers(doc):
        matcher = Matcher(doc.vocab)
        pattern = [{'TEXT': {'REGEX': '(\+)?(\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'}}]
        matcher.add('PHONE_NUMBER', [pattern])
        print(matches)
        matches = matcher(doc)
        spans = []
        for start, end in matches:
            span = doc[start:end]
            spans.append(span)
        for span in spans:
            email_ent = Span(doc, span.start, span.end, label="PHONE_NUMBER")
            doc.ents = list(doc.ents) + [email_ent]
        return doc
    
    @Language.component("remove_gpe")
    def clean_types(doc):
        original_ents = list(doc.ents)
        for ent in doc.ents:
            if ent.label_ == "QUANTITY":
                original_ents.remove(ent)
            elif ent.label_ == "CARDINAL":
                original_ents.remove(ent)
            elif ent.label_ == "EVENT":
                original_ents.remove(ent)
            elif ent.label_ == "TIME":
                original_ents.remove(ent)
            elif ent.label_ == "MONEY":
                original_ents.remove(ent)
            elif ent.label_ == "PERCENT":
                original_ents.remove(ent)
            elif ent.label_ == "PRODUCT":
                original_ents.remove(ent)
            elif ent.label_ == "PERSON":
                original_ents.remove(ent)
            elif ent.label_ == "DATE":
                original_ents.remove(ent)
        doc.ents = original_ents
        return doc

