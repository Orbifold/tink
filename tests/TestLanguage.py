# -*- coding: utf-8 -*-


import unittest
from nose.tools import assert_equal, nottest, assert_raises

from ..Language import Language


class TestLanguage(unittest.TestCase):

    def test_get_verbs(self):
        nl_verbs = Language.get_verbs("ik ga naar de winkel en ben hongerig", lang="nl")
        assert_equal(len(nl_verbs), 2)
        assert {"ga", "ben"} == {token.text for token in nl_verbs}

        en_verbs = Language.get_verbs("I will go tomorrow and buy it for you")
        assert_equal(len(en_verbs), 3)
        assert {"will", "go", "buy"} == {token.text for token in en_verbs}

    def test_get_nouns(self):
        nl_nouns = Language.get_nouns("ik ga naar de winkel met mijn mooie wagen", lang="nl")
        assert_equal(len(nl_nouns), 2)
        assert {"winkel", "wagen"} == {token.text for token in nl_nouns}

        en_nouns = Language.get_nouns("My car is so pretty.")
        assert_equal(len(en_nouns), 1)
        assert {"car"} == {token.text for token in en_nouns}

    def test_is_noun(self):
        assert Language.is_noun("machine")
        assert Language.is_noun("table")
        assert Language.is_noun("tafel", lang="nl")
        assert not Language.is_noun("werken", lang="nl")

    def test_is_verb(self):
        assert Language.is_verb("tuning")
        assert Language.is_verb("riding")
        assert Language.is_verb("wandelen", lang="nl")
        assert not Language.is_verb("meesterwerk", lang="nl")

    def test_cleanup(self):
        assert len(Language.cleanup_text("...")) == 0
        # removes idle spaces and punctuation
        assert_equal(Language.cleanup_text("This,  and:   that!"),"This and that")


    def test_synonyms(self):
        input = ["wijsheid", "eten"]
        # for i in input:
        #     print(Language.get_synonyms(i, "nl"))
        assert Language.get_synonyms("wijsheid", "nl") is not None
        assert Language.get_synonyms("eten", "nl") is not None
        assert Language.get_synonyms("eat", "en") is not None
        assert Language.get_synonyms("wisdom", "en") is not None
