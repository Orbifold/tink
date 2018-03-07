import re

from .Language import *

shapex = re.compile("((?=^)|\s)%\w+(\_)?(\:((\([\w,\s]+\))|\w+))?", re.I)
capx = re.compile("((?=^)|\s)(%\w+(\_)?(\:((\([\w,\s]+\))|\w+))?)")


class TypeConstraints():
    """
        Collects the methods which tell whether the giving value can be accepted.
        When a parameter '%name_something' is present there should be a method in this class
        called 'is_something' returning True/False and all else happens automatically.
    """

    @staticmethod
    def is_verb(value):
        """
            Accepts the given value if it's recognized as a verb.
            Note that some words can be both noun and verb, this method
            is not bullet-proof.

        :param value: the parameter value.
        :return: True if the value is a verb.
        """
        return Language.is_verb(value)

    @staticmethod
    def is_cool(value):
        """
            Sample fitting the word 'cool' and nothing else.
        """
        return value.lower() == "cool"


class Parameter():
    """
        A matching parameter.
        Corresponding to something in the shape of '%name_type:default'.
    """

    def __init__(self, name):
        self.name = name
        self.value = None
        self.type = None
        self.default = None


class Match():
    """
    The result of a pattern matching.
    """

    def __init__(self, pattern, input):
        self.parameters = []
        self.pattern = pattern
        self.input = input
        for p in Patterns._collect_parameters(pattern):
            self.parameters.append(p)

    @property
    def get_values(self):
        """
            Gets the values of the parameters.

        :return: a list of parameter values.
        """
        return [p.value for p in self.parameters]

    def get_parameter(self, name):
        """
            Gets the parameter with the specified name.

        :param name: The name of the parameter.
        :return: a Parameter object
        """
        found = [p for p in self.parameters if p.name == name]
        if len(found) > 0:
            return found[0]
        else:
            return None

    def has_value(self, name):
        """
            Returns whether the parameter with the specified name has a value.

        :param name: a parameter name.
        :return: True the parameter is not None
        """
        p = self.get_parameter(name)
        if p is None:
            return False
        else:
            return p.value is not None

    def parameter_exists(self, name):
        """
            Returns whether there is a parameter with the specified name.

        :param name:
        :return:
        """
        return self.get_parameter(name) is not None

    def get_value(self, name):
        """
            Gets the value of the parameter with the given name.

        :param name: a parameter name
        :return: the value or None
        """
        p = self.get_parameter(name)
        if p is None:
            return None
        else:
            return p.value

    def __str__(self):
        return "' ".join([f"{p.name}: {p.value}" for p in self.parameters])


class Patterns():
    """
        Orchestrates the matching process.
    """

    @staticmethod
    def _make_regex(pattern):
        """
            Turns the pattern in a regex.

        :param pattern: a pattern to match input.
        :return: the regex corresponding to the pattern.
        """
        rex = "^" + re.sub(shapex, "(.*?)", pattern) + "$"
        return rex

    @staticmethod
    def is_match(pattern, input):
        """
            Matches without looking at type constraints.

        :param pattern: a pattern to match input.
        :param input: any input.
        :return: True if pattern and input match.
        """

        # starting with a parameter needs an extra space in order to match
        # '^(.*?) is sunny$' will otherwise not match 'is sunny'

        if pattern[0] == "%":
            input = " " + input
        return re.match(Patterns._make_regex(pattern), input) is not None

    @staticmethod
    def _collect_parameters(pattern):
        """
            Picks up the parameters from the pattern.

        :param pattern: a pattern.
        :return: a list of Parameter instances.
        """
        found = re.findall(capx, pattern)
        # the index 1 means the second selection group
        return [Patterns._get_param_definition(x[1]) for x in found]

    @staticmethod
    def _get_input_tokens(input, lang="en"):
        """
            Gets the Spacy tokens to be used in the matching process.

        :param input: any input.
        :param lang: the language of the input, default "en".
        :return:
        """
        # stack = re.split(r"[\s:]+", s)
        # no cleanup because it's been done in the process method
        stack = Language.get_doc(input, lang, False)
        stack.reverse()
        return stack

    @staticmethod
    def _get_pattern_stack(pattern):
        """
            Returns the stack of words and parameters
            to be used in the matching process.
        :param pattern: a pattern.
        :return:
        """
        stack = re.split(r"\s+", pattern)
        stack.reverse()
        return stack

    @staticmethod
    def _get_param_definition(param):
        """
            Turns the raw parameter into its components.

        :param param: a raw parameter (in the shape %name_type:default).
        :return:
        """
        defparts = param.split(":")
        pdef = defparts[1] if len(defparts) > 1 else None
        typeparts = defparts[0].split("_")
        tdef = typeparts[1] if len(typeparts) > 1 else None
        if pdef is not None and pdef[0] == "(":
            pdef = pdef[1:-1]
        name = typeparts[0].replace("%", "")
        p = Parameter(name)
        p.default = pdef
        p.type = tdef
        return p

    @staticmethod
    def _assign_if_valid(parameter, value):
        """
            Checks whether the given value fits the type constraint, if any.
            If so the value is assigned to the parameter.

        :param parameter: a parameter object.
        :param value: the potential value to test against the constraint.
        """
        if parameter.type is None:
            parameter.value = value
        else:
            if f"is_{parameter.type}" in vars(TypeConstraints).keys():
                if vars(TypeConstraints)[f"is_{parameter.type}"].__func__(value):
                    parameter.value = value

            else:
                raise Exception(f"The type '{parameter.type}' is not implemented as a type constraint.")

    @staticmethod
    def _fill_defaults(match):
        """
            Applies default values to the unmatched parameters.

        :param match: a Match instance
        """
        for p in match.parameters:
            if p.value is None and p.default is not None:
                p.value = p.default

    @staticmethod
    def _get_parameter_name(raw_param):
        """
            Extracts the name of the parameter from the raw definition.
            That is, the mapping from '%name_type:default' to 'name'.

        :param raw_param: a raw parameter.
        :return: a parameter name
        """
        if raw_param.find("_") > 0:
            return raw_param.split("_")[0]
        else:
            if raw_param.find(":") > 0:
                return raw_param.split(":")[0]
            else:
                return raw_param

    @staticmethod
    def _extract(pattern, input, lang="en"):
        """
            The actual process of matching a pattern and an input.
            This process will only start if a prior check via 'is_match' worked.

        :param pattern: a pattern.
        :param input: some input.
        :param lang: the languahe of the input, default "en".
        :return: a Match instance.
        """
        match = Match(pattern, input)

        stack = Patterns._get_input_tokens(input, lang)
        d = Patterns._get_pattern_stack(pattern)
        v = ""
        t = d.pop()
        collect = False
        paramName = 1
        while len(stack) > 0:
            token = stack.pop()
            if token.text == t:
                collect = False
                if v is not None and len(v) > 0:
                    p = match.get_parameter(paramName)
                    # this will check possible constraints
                    Patterns._assign_if_valid(p, v.strip())
                    v = ""

                if len(d) > 0:
                    t = d.pop()
                elif len(stack) > 0 and t != "*":
                    raise Exception(f"Matching went wrong with '{pattern}'.")
            else:
                if t.find("%") == 0:
                    paramName = Patterns._get_parameter_name(t[1:])
                    if len(d) > 0:
                        t = d.pop()
                    # t is now possibly the next word which matches the token
                    # which means the parameter is blank (or the default if set)
                    if t != token.text:
                        collect = True
                        v += " " + token.text

                else:
                    if collect:
                        v += " " + token.text
                    else:
                        if len(d) > 0:
                            t = d.pop()
        if v is not None and len(v) > 0:
            p = match.get_parameter(paramName)
            # this will check possible constraints
            Patterns._assign_if_valid(p, v.strip())
        Patterns._fill_defaults(match)
        return match

    @staticmethod
    def fit(pattern, input, lang="en"):
        """
            Attempts to match the given pattern with the input.

            A pattern has parameters which accept one or more words from the input. For example:

                "%name is home"

            will fit the input

                "Jan is home"

            and return "Jan" as a value for the parameter "name". A parameter can furthermore have type constraints like

                "%name_noun is home" or "A car with number %num_carplate"

            provided that there is a constraint function implemented for the type.

            A parameter can also accept a default value like so

                "I like %more:fresh bread"


        :param pattern: A pattern. DO NOT use punctuation in the pattern.
        :param input: Any string.
        :param lang: The language; 'en' by default.
        :return:
        """
        if input is None:
            raise Exception("No input given.")
        input = input.strip()
        if len(input) == 0:
            raise Exception("No input given.")
        cleaned_input = Language.cleanup_text(input, lang)
        if len(cleaned_input) == 0:
            raise Exception("The input contained no information.")

        if Patterns.is_match(pattern, cleaned_input):
            return Patterns._extract(pattern, cleaned_input)
        else:
            return None
