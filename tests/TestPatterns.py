# -*- coding: utf-8 -*-


import unittest
from nose.tools import assert_equal, nottest

from ..Language import Language
from ..Patterns import Patterns


class TestPatterns(unittest.TestCase):

    def test_patterns1(self):
        e = Patterns.fit("%a is %b", "a tree is a plant")
        assert_equal(len(e.parameters), 2)
        assert_equal({"a tree", "a plant"}, {x.value for x in e.parameters})
        e = Patterns.fit("%a is %b", "a tree is a plant")
        assert_equal(len(e.parameters), 2)
        assert e.parameter_exists("a")
        assert not e.parameter_exists("something")
        assert_equal(e.get_value("a"), "a tree")
        assert_equal(e.get_value("b"), "a plant")
        assert e.get_value("something") is None

    def test_multiword_fit(self):
        m = Patterns.fit("%a treat", "This cake is a real treat!")
        assert m is not None
        assert_equal("This cake is a real", m.get_value("a"))

    def test_is_match(self):
        # note that is_match does not check type constraints, this is done via the Patterns.fit method.
        # Also, punctuation is part of the fit method and not in is_match.
        assert Patterns.is_match("%a_string is great", "Sunny holidays is great")
        assert Patterns.is_match("my name is %name_something", "my name is Lela.")
        assert Patterns.is_match("%s treat", "this sweet is a real treat")
        assert not Patterns.is_match("love is like a rose", "the cake is lovely")

    def test_is_cool(self):
        e = Patterns.fit("%a is %b_cool", "Jam is Cool")
        assert e.get_value("b") == "Cool"
        e = Patterns.fit("%a is %b_cool", "Whiskey is delicious")
        assert e.get_value("b") is None

    def test_defaults(self):
        m = Patterns.fit("I like %more:fresh bread", "I like bread.")
        assert m is not None
        assert_equal(m.get_value("more"), "fresh")

        m = Patterns.fit("%a:Sunday is sunny", "is sunny.")
        assert m is not None
        assert_equal(m.get_value("a"), "Sunday")
