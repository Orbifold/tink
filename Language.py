import csv
from itertools import chain

from nltk.corpus import wordnet

from .Resources import *


class Language():
    """
        Standard language functionality.
    """

    @staticmethod
    def _cleanup_text(doc):
        """
            Removes punctuation and unwanted spaces from the Spacy doc.
        :param doc: a Spacy document
        :return: a list of Spacy tokens
        """
        # if you don't want the digits use in addition
        #   | token.is_digit
        return [token for token in doc if not (token.is_punct | token.is_space)]

    @staticmethod
    def cleanup_text(text, lang="en"):
        """
            Returns the given text without punctuation and idle spaces.
        :param text: any text
        :param lang: The language; 'en' by default.
        :return: the cleaned up text.
        """
        doc = Language.get_doc(text, lang, True)
        return " ".join([token.text for token in doc])

    @staticmethod
    def _search_nl_synonym(word):
        """
            Returns NL synonyms.
            Based on data from http://data.opentaal.org/opentaalbank/thesaurus/

        :param word: any word
        :return: the list of synonyms
        """
        res_dir = Resources.get_resources_dir()
        p = os.path.join(res_dir, "thesaurus.nl.txt")
        with open(p, 'rt', encoding='utf-8', errors='ignore') as f:
            rd = csv.reader(f, delimiter=";")
            for row in rd:
                if row[0].lower() == word.lower():
                    return row
            return None

    @staticmethod
    def get_doc(text, lang="en", cleanup=True):
        """
            Gets the Spacy doc for the given text and language.

        :param text: Any text.
        :param lang: The language; 'en' by default.
        :return: a Spacy document
        """
        if lang.lower() == "en":
            elp = Resources.elp()
            doc = elp(text)
        elif lang.lower() == "nl":
            nlp = Resources.nlp()
            doc = nlp(text)
        else:
            raise Exception(f"Language '{lang}' is not supported.")

        if cleanup == True:
            return Language._cleanup_text(doc)
        else:
            return [token for token in doc]

    @staticmethod
    def get_verbs(text, lang="en"):
        """
            Returns the tokens in the given text with POS tagged as verb.

        :param text: Any text.
        :param lang: The language; 'en' by default.
        :return: a list of tokens
        """
        doc = Language.get_doc(text, lang)
        return [word for word in doc if word.pos_ == "VERB"]

    @staticmethod
    def get_nouns(text, lang="en"):
        """
            Returns the tokens in the given text with POS tagged as noun.

        :param text: Any text.
        :param lang: The language; 'en' by default.
        :return: a list of tokens
        """
        doc = Language.get_doc(text, lang)
        return [word for word in doc if word.pos_ == "NOUN"]

    @staticmethod
    def is_verb(text, lang="en"):
        """
            Returns whether the given word is a verb.
            If more than one word is given the first word is picked out.
            Note that some words like 'love' can be both a verb and a noun.

        :param text: Any text.
        :param lang: The language; 'en' by default.
        :return: TRUE if the word is a verb.
        """
        doc = Language.get_doc(text, lang)
        return doc[0].pos_ == "VERB"

    @staticmethod
    def is_noun(text, lang="en"):
        """
            Returns whether the given word is a noun.
            If more than one word is given the first word is picked out.

        :param text: Any text.
        :param lang: The language; 'en' by default.
        :return: TRUE if the word is a noun.
        """
        doc = Language.get_doc(text, lang)
        return doc[0].pos_ == "NOUN"

    @staticmethod
    def get_synonyms(word, lang="en"):
        """
            Returns synonyms of the given word.
            The Dutch scope is limited due to lack of data but the current
            implementation is a flat text file and easily extensible.

        :param word: A single word is expected.
        :param lang: The language; 'en' by default.
        :return: A list of synonyms.
        """
        if lang == "en":
            synonyms = wordnet.synsets(word)
            lemmas = set(chain.from_iterable([word.lemma_names() for word in synonyms]))
            return [syn.replace("_", " ") for syn in list(lemmas)]
        elif lang == "nl":
            return Language._search_nl_synonym(word)
        else:
            raise Exception(f"Language '{lang}' is not supported.")

