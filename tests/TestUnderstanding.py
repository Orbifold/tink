# -*- coding: utf-8 -*-


import unittest
from nose.tools import assert_equal, nottest

from ..Language import Language
from ..Understanding import Understanding, SVOExtractor


class TestUnderstanding(unittest.TestCase):

    def test_dependency_dutch(self):
        input = "Jan en Jos zijn met de wagen weggegaan naar Leusden."
        dep = Understanding.get_dependency(input, lang="nl")
        assert dep is not None
        assert dep.root.word == "weggegaan"
        print(dep)

    def test_dependency_english(self):
        input = "John and Levi went to Brussels by car."
        dep = Understanding.get_dependency(input, lang="en")
        assert dep is not None
        assert dep.root.word == "went"
        print(dep)

    def test_get_entities(self):
        input = "John Walter went to Liverpool by train."
        ners = Understanding.get_entities(input, "en")
        assert len(ners) == 2
        assert_equal({n.entity for n in ners}, {"John Walter", "Liverpool"})

        input = "Jan Bosman reisde dan verder naar Rome en Milaan."
        ners = Understanding.get_entities(input, "nl")
        assert len(ners) == 3
        assert_equal({n.entity for n in ners}, {"Jan Bosman", "Rome", "Milaan"})

    def test_get_verbs(self):
        input = "He told me i would die alone with nothing but my career someday."
        verbs = Understanding.get_verbs(input)
        assert len(verbs) == 2
        assert_equal({"die", "told"}, {t.word for t in verbs})
        dep = Understanding.get_dependency(input)
        print(dep)
        assert_equal(dep.root.word, "told")
        assert_equal(dep.root.lemma, "tell")

        input = "Ze vertelde me alles en hoe gelukkig de kinderen zijn."
        verbs = Understanding.get_verbs(input, "nl")
        assert len(verbs) == 2
        assert_equal({"vertelde", "zijn"}, {t.word for t in verbs})
        dep = Understanding.get_dependency(input, "nl")
        print(dep)
        assert_equal(dep.root.word, "vertelde")
        assert_equal(dep.root.lemma, "vertellen")

    def test_lefts_rights(self):
        dep = Understanding.get_dependency("He says that you like to swim.")
        print(dep)
        node = dep.get_node("like")
        assert node is not None
        assert_equal({"that", "you"}, {t.word for t in node.lefts})
        assert_equal({"swim"}, {t.word for t in node.rights})

        dep = Understanding.get_dependency("Hij zegt dat je houdt van zwemmen.", "nl")
        print(dep)
        node = dep.get_node("zegt")
        assert node is not None
        assert_equal({"Hij"}, {t.word for t in node.lefts})
        assert_equal({"houdt"}, {t.word for t in node.rights})

    def test_get_sv_en(self):
        input = "He says that you like to swim."
        svo = SVOExtractor(input)
        found = svo._get_sv()
        print(found)
        print(svo.tree)
        assert len(found) == 1

        input = "Peter and Fred went on holidays to France."
        svo = SVOExtractor(input)
        found = svo._get_sv()
        print(found)
        assert len(found) == 1
        assert_equal(found[0]["verb"], "went")
        assert_equal(set(found[0]["subject"]), {"Fred", "Peter"})

    def test_get_vo_en(self):
        input = "Lynda owns a car."
        svo = SVOExtractor(input)
        found = svo._get_vo()
        print(svo.tree)
        assert len(found) == 1
        assert_equal(set(found[0]["object"]), {"car"})

        input = "Johnny put the weapon in the garage."
        svo = SVOExtractor(input)
        print(svo.tree)
        found = svo._get_vo()
        print(found)
        assert_equal(set(found[0]["object"]), {"weapon", "garage"})

        input = "I have carried your gods and ideas."
        svo = SVOExtractor(input)
        print(svo.tree)
        found = svo._get_vo()
        assert_equal(set(found[0]["object"]), {"gods", "ideas"})

        input = "Tom entered the empty room with anger and dispair."
        svo = SVOExtractor(input)
        print(svo.tree)
        found = svo._get_vo()
        assert_equal(set(found[0]["object"]), {"room", "anger", "dispair"})

    def test_get_svo_en(self):
        def process(input):
            svo = SVOExtractor(input)
            print(svo.tree)
            return svo.extract_svo()

        inputs = [
            "I went home.",
            "he did not kill me",
            "George drove to the factory.",
            "he and his brother shot me and my sister",
            "Fred brought the kids to school!",
            "I have no other financial assistance available, and he certainly will not provide support."
        ]
        for input in inputs:
            print(process(input))

    def test_get_sv_nl(self):
        input = "Ze zegt dat je niet naar huis wil gaan."
        svo = SVOExtractor(input, "nl")
        found = svo._get_sv()
        print(found)
        print(svo.tree)
        assert len(found) == 1
        assert_equal({x["verb"] for x in found}, {"zegt"})
        assert_equal({x["subject"][0] for x in found}, {"Ze"})

        input = "George fietst langzaam naar het water"
        svo = SVOExtractor(input, "nl")
        found = svo._get_sv()
        print(found)
        assert len(found) == 1
        assert_equal({x["verb"] for x in found}, {"fietst"})
        assert_equal({x["subject"][0] for x in found}, {"George"})

        input = "Ina en Linde waren goede buren tot dit gebeurde."
        svo = SVOExtractor(input, "nl")
        found = svo._get_sv()
        print(svo.tree)
        print(found)
        assert len(found) == 1
        assert_equal({x["verb"] for x in found}, {"gebeurde"})
        # assert_equal({x["subject"][0] for x in found}, {"George"})

    def test_get_svo_nl(self):
        input = "Janna heeft een rode wagen en een fiets."
        svo = SVOExtractor(input, "nl")
        found = svo._get_vo()
        print(found)
        assert len(found) == 1
        assert_equal(set(found[0]["object"]), {"wagen", "fiets"})
        svo = svo.extract_svo()
        assert_equal(svo, [(['Janna'], 'heeft', ['wagen', 'fiets'])])

        input = "Janna en Roos hebben samen een nieuw avontuur in Thailand."
        svo = SVOExtractor(input, "nl")
        svo = svo.extract_svo()
        assert_equal(svo, [(['Janna', 'Roos'], 'hebben', ['samen', 'avontuur', 'Thailand'])])

    def test_get_tokens_de(self):
        input = "ich bin so glücklich mit meinem mann"
        svo = SVOExtractor(input, "de")
        found = svo.extract_svo()
        print(svo.tree)
        print(found)
        assert_equal([(['ich'], 'glücklich', ['mann'])], found)
        """
        input: 
        
            ich bin so glücklich mit meinem mann
        
        dependency:
        
            glücklich [root, ADJ]
                + ich [nsubj, PRON]
                + bin [cop, VERB]
                + so [advmod, ADV]
                + mann [nmod, NOUN]
                    + mit [case, ADP]
                    + meinem [det:poss, PRON]
        
        triple:
            
            [(['ich'], 'glücklich', ['mann'])]
        """

    def test_get_tokens_fr(self):
        input = "je suis allé à la maison"
        svo = SVOExtractor(input, "fr")
        found = svo.extract_svo()
        print(svo.tree)
        print(found)
        assert_equal([(['je'], 'allé', ['maison'])], found)
