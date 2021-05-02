import pytest

from pymkup import Pymkup

pytest.filename = "/tests/markup-deep-spaces.pdf"


def test_spaces_returned_dict():
    x = Pymkup(pytest.filename)
    spaces = x.spaces()
    assert 'spaces' in spaces


def test_markup_returned_dict():
    x = Pymkup(pytest.filename)
    markup = x.markups()
    assert 'markups' in markup
