from .Resources import *
import os

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl", "conj"]
OBJECTS = [ "obj", "dative", "attr", "oprd", "prep", "ccomp", "conj", "advmod"]


class SVOBase():
    """
        Base class for SVO extraction.
    """
    def __init__(self, input, lang):
        """
            Creates a new instance.
        :param input: any text.
        :param lang: the language of the given text.
        """
        self.input = input
        self.tree = Understanding.get_dependency(input, lang)

    def _get_objects_from_prepositions(self, deps):
        """
            Preposition: a word governing, and usually preceding, a noun or pronoun and expressing a relation to another word or element in the clause,
            as in ‘the man on the platform’, ‘she arrived after dinner’, ‘what did you do it for ?’.
        :param deps:
        :return:
        """
        objs = []
        for dep in deps:
            if dep.pos == "ADP" and dep.dep == "prep":
                objs.extend([tok for tok in dep.rights if tok.dep in OBJECTS or (tok.pos == "PRON" and tok.word.lower() == "me")])
        return objs

    def _get_objects_from_xcomps(self, deps):
        """
            xcomp: An open clausal complement (xcomp) of a verb or an adjective is a predicative or clausal complement without its own subject.
            The reference of the subject is necessarily determined by an argument external to the xcomp (normally by the object of the next higher clause,
            if there is one, or else by the subject of the next higher clause. These complements are always non-finite, and they are complements
            (arguments of the higher verb or adjective)
            rather than adjuncts/modifiers, such as a purpose clause.

        :param deps:
        :return:
        """
        for dep in deps:
            if dep.pos == "VERB" and dep.dep == "xcomp":
                v = dep
                rights = list(v.rights)
                objs = [tok for tok in rights if tok.dep in OBJECTS]
                objs.extend(self._get_objects_from_prepositions(rights))
                if len(objs) > 0:
                    return v, objs
        return None, None

    def _get_objects_from_conjunctions(self, objects):
        more_objs = []
        for obj in objects:
            rights = obj.rights
            more_objs.extend([tok for tok in rights if tok.dep in OBJECTS or tok.pos == "NOUN"])
            if len(more_objs) > 0:
                more_objs.extend(self._get_objects_from_conjunctions(more_objs))
        return more_objs

    def _get_objects(self, verb):
        rights = verb.rights
        objs = [tok for tok in rights if tok.dep in OBJECTS]
        objs.extend(self._get_objects_from_prepositions(rights))
        potential_new_verb, potential_new_objs = self._get_objects_from_xcomps(rights)
        if potential_new_verb is not None and potential_new_objs is not None and len(potential_new_objs) > 0:
            objs.extend(potential_new_objs)
            verb = potential_new_verb
        if len(objs) > 0:
            objs.extend(self._get_objects_from_conjunctions(objs))
        return verb, objs

    def _get_verbs(self):
        """
            Gets the (non-auxilliary) verbs.
            Note that these are the starting verbs for triple extraction and is not the same
            as getting the POS verbs.
        :return:
        """
        return [node for node in self.tree.nodes if node.pos == "VERB" and node.pos != "AUX"]

    def _is_negated(self, token):
        """
            Looks for lefts and rights whether a negating token is present.
        :param token: A doc token.
        :return:
        """
        negations = {"no", "not", "n't", "never", "none"}
        for dep in token.lefts + token.rights:
            if dep.word.lower() in negations:
                return True
        return False

    def _get_subjects_from_conjunctions(self, subs):
        """
            Looks for additional subjects bound to the given ones via things like 'and' in 'Peter and Fred went...'
        :param subs: first-level subjects
        :return: The augmented set of subjects.
        """
        more_subs = []
        for sub in subs:
            rights = sub.rights
            more_subs.extend([tok for tok in rights if tok.dep in SUBJECTS or tok.pos == "NOUN" or tok.pos == "PROPN"])
            if len(more_subs) > 0:
                more_subs.extend(self._get_subjects_from_conjunctions(more_subs))
        return more_subs

    def _get_subjects(self, verb):
        """
            Returns the subjects for the given verb.

        :param verb:
        :return:
        """
        verb_is_negated = self._is_negated(verb)
        subs = [tok for tok in verb.lefts if tok.dep in SUBJECTS and tok.pos != "DET"]
        if len(subs) > 0:
            subs.extend(self._get_subjects_from_conjunctions(subs))
        else:
            found_subs, verb_is_negated = self.find_subjects(verb)
            subs.extend(found_subs)
        return subs, verb_is_negated

    def find_subjects(self, tok):
        head = tok.parent
        while head.pos != "VERB" and head.pos != "NOUN" and head.parent != head:
            head = head.parent
        if head.pos == "VERB":
            subs = [tok for tok in head.lefts if tok.dep == "SUB"]
            if len(subs) > 0:
                verb_negated = self._is_negated(head)
                subs.extend(self._get_subjects_from_conjunctions(subs))
                return subs, verb_negated
            elif head.parent != head:
                return self.find_subjects(head)
        elif head.pos == "NOUN":
            return [head], self._is_negated(tok)
        return [], False

    def extract_svo(self):
        """
            Returns SVO triples.
        :return: A list of triples.
        """
        svos = []
        verbs = self._get_verbs()
        for verb in verbs:
            subjects, verb_negated = self._get_subjects(verb)
            # hopefully there are subs, if not, don't examine this verb any longer
            if len(subjects) > 0:
                verb, objs = self._get_objects(verb)
                for subject in subjects:
                    for obj in objs:
                        obj_negated = self._is_negated(obj)
                        svos.append((subject.word.lower(), "!" + verb.word.lower() if verb_negated or obj_negated else verb.word.lower(), obj.word.lower()))
        return svos

    def _get_sv(self):
        verbs = self._get_verbs()
        r = []
        for verb in verbs:
            subs = self._get_subjects(verb)
            if subs is None: continue
            r.append({
                "verb": verb.word,
                "subject": [t.word for t in subs[0]]
            })
        return r

class DutchSVO(SVOBase):

    def __init__(self, input):
        super().__init__(input, "nl")

    def get_svo(self):
        pass


class EnglishSVO(SVOBase):

    def __init__(self, input):
        super().__init__(input, "en")



    def _get_vo(self):
        verbs = self._get_verbs()
        r = []
        for verb in verbs:
            objs = self._get_objects(verb)
            if objs is None: continue
            r.append({
                "verb": verb.word,
                "object": [t.word for t in objs[1]]
            })
        return r

    def get_svo(self):
        pass


class NamedEntity():
    """
        Captures the details of a named entity.
    """

    def __init__(self, spacy_token):
        self.entity = spacy_token.text
        self.start = spacy_token.start_char
        self.end = spacy_token.end_char
        self.type = spacy_token.label_


class Dependency():
    """
        Captures the dependency tree of a sentence.
    """

    def __init__(self, nodes):
        self.nodes = nodes
        self.root = self._build_tree(nodes)

    def _find_id(self, id):
        found = list(filter(lambda x: x.id == id, self.nodes))
        if len(found) == 1:
            return found[0]
        else:
            return None

    def _build_tree(self, nodes):
        root = None
        for node in nodes:
            id = node.id
            item = self._find_id(id)
            if item is None:
                raise Exception("Could not find the item")
            if node.parentId > 0:
                parent = self._find_id(node.parentId)
                parent.children.append(item)
                item.parent = parent
            else:
                root = item
        for node in nodes:
            node.root = root
        root.parent = root
        return root

    def get_node(self, word):
        """
            Returns the node corresponding to the given word, if any.
        :param word: A word supposedly contained in the input.
        :return: The token, if found.
        """
        for node in self.nodes:
            if node.word.lower() == word:
                return node
        return None

    def __str__(self):
        def show_node(node, level, s):
            indent = '\t'.expandtabs(level * 4)
            if level == 0:
                s += f"{indent}{node.word} [{node.dep}, {node.pos}]"
            else:
                s += f"\n{indent}+ {node.word} [{node.dep}, {node.pos}]"
            if len(node.children) > 0:
                for n in node.children:
                    s = show_node(n, level + 1, s)
            return s

        return show_node(self.root, 0, "")

    def get_verbs(self):
        return [t for t in self.nodes if t.pos == "VERB"]


class Token():
    """
        Represents a node in a dependency tree or POS parsing.
        The children-parent relationships are only available if the node is created as
        part of a dependency parsing.
    """

    def __init__(self, deprow):
        self.children = []
        self.parent = None
        self.id = int(deprow[0])
        self.word = deprow[1]
        self.lemma = deprow[2]
        self.pos = deprow[3]
        self.pos2 = deprow[4]
        self.pos3 = deprow[5]
        self.parentId = int(deprow[6])
        self.dep = deprow[7]
        self.root = None

    @property
    def is_root(self):
        return self.dep == 0

    @property
    def lefts(self):
        return [l for l in self.children if l.id < self.id and l.pos != "PUNCT"]

    @property
    def rights(self):
        return [l for l in self.children if l.id > self.id and l.pos != "PUNCT"]

    def __str__(self):
        return f"{self.word}"


class Understanding():
    """
        Collects diverse functions which go beyond the basic language functionalities.
    """
    en_pipeline = None
    nl_pipeline = None

    def __init__(self):
        pass

    def stringify(s):
        if isinstance(s, str):
            return s
        else:
            return str(s, 'utf-8')

    @staticmethod
    def _get_udpipe_pipeline(lang):
        if lang == "en":
            if Understanding.en_pipeline is None:
                from ufal.udpipe import Pipeline
                model = Resources.get_udpipe_model(lang)
                Understanding.en_pipeline = Pipeline(model, "generic_tokenizer", Pipeline.DEFAULT, Pipeline.DEFAULT, "")
            return Understanding.en_pipeline
        elif lang == "nl":
            if Understanding.nl_pipeline is None:
                from ufal.udpipe import Pipeline
                model = Resources.get_udpipe_model(lang)
                Understanding.nl_pipeline = Pipeline(model, "generic_tokenizer", Pipeline.DEFAULT, Pipeline.DEFAULT, "")
            return Understanding.nl_pipeline
        else:
            raise Exception(f"Language '{lang}' is not supported.")

    @staticmethod
    def get_dependency(input, lang="en"):
        nodes = Understanding.get_tokens(input, lang)
        return Dependency(nodes)

    @staticmethod
    def get_tokens(input, lang="en"):
        from io import StringIO
        from ufal.udpipe import ProcessingError
        error = ProcessingError()
        pipeline = Understanding._get_udpipe_pipeline(lang)
        processed = pipeline.process(input, error)
        if error.occurred():
            raise Exception(error.message)
        sio = StringIO(processed)
        # pandas frame is a bit overkill I guess
        # import pandas as pd
        #  first three rows has comments
        # df = pd.read_csv(sio, sep="\t", skiprows=3)
        # return df
        import csv
        rd = csv.reader(sio, delimiter="\t")

        nodes = []
        for row in rd:
            if len(row) < 8:
                continue
            nodes.append(Token(row))
        return nodes

    @staticmethod
    def get_entities(input, lang="en"):
        """
            Returns the named entities found in the given input.
        :param input: Any text.
        :param lang: The language of the input.
        :return: A list of NamedEntity objects.
        """
        mlp = Resources.get_spacy_model(lang)
        doc = mlp(input)
        result = []
        for ent in doc.ents:
            result.append(NamedEntity(ent))
        return result

    @staticmethod
    def get_verbs(input, lang="en"):
        """
            Returns the verbs as defined by POS.
            Note that this has no relation to the verbs from the triple extraction.
            See the "get_dependency_verbs".
        :param input: Any text.
        :param lang: The language of the input.
        :return: A list of tokens.
        """
        nodes = Understanding.get_tokens(input, lang)
        return [t for t in nodes if t.pos == "VERB"]

    @staticmethod
    def get_dependency_verbs(input, lang="en"):
        tree = Understanding.get_dependency(input, lang)
        return tree.get_verbs()

    @staticmethod
    def get_svo(input, lang="en"):
        """
            Returns the subjects-verb-object triples in the given input.

        :param input: Any text
        :param lang: The language of the input.
        :return: A list of 3-tuples
        """
        if lang == "en":
            worker = EnglishSVO(input)
            return worker.get_svo()
        elif lang == "nl":
            worker = DutchSVO(input)
            return worker.get_svo()
        else:
            raise Exception(f"Language '{lang}' is not supported.")
