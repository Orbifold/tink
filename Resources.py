import pathlib
import os

import spacy

class Resources():
    """
        Access to resources and static models.
    """
    _elp = None
    _nlp = None
    en_model = None
    nl_model = None

    @staticmethod
    def get_udpipe_model(lang):
        """
            Static ref to a UDPipe model.
            The actual models are in the data directory.
        """
        from ufal.udpipe import Model, Pipeline
        res_path = Resources.get_resources_dir()

        if lang == "en":
            if Resources.en_model is None:
                Resources.en_model = Model.load(os.path.join(res_path, "english-ud-2.1-20180111.udpipe"))
                if Resources.en_model is None:
                    raise Exception("Failed to load the English UDPipe model.")
            return Resources.en_model

        elif lang == "nl":
            if Resources.nl_model is None:
                Resources.nl_model = Model.load(os.path.join(res_path, "dutch-ud-2.1-20180111.udpipe"))
                if Resources.nl_model is None:
                    raise Exception("Failed to load the Dutch UDPipe model.")
            return Resources.nl_model
            # return Model.load(os.path.join(res_path, "dutch-ud-2.1-20180111.udpipe"))
        else:
            raise Exception(f"Language '{lang}' is not supported.")

    @staticmethod
    def elp():
        """
            Static ref to the English Spacy model
        """
        if Resources._elp is None:
            Resources._elp = spacy.load("en")
        return Resources._elp

    @staticmethod
    def nlp():
        """
            Static ref to the Dutch Spacy model
        """
        if Resources._nlp is None:
            Resources._nlp = spacy.load("nl")
        return Resources._nlp

    @staticmethod
    def get_spacy_model(lang="en"):
        if lang == "en":
            return Resources.elp()
        elif lang == "nl":
            return Resources.nlp()
        else:
            raise Exception(f"Language '{lang}' is not supported.")

    @staticmethod
    def get_resources_dir():
        """
            Gets the absolute path of the Resources dir.
        :return: The Resources path.
        """
        parent_dir = pathlib.Path(__file__).parent
        return os.path.join(parent_dir, "data")
