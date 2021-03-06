import pytest

from pymkup import Pymkup

pytest.filename = "/tests/markup-deep-spaces.pdf"


def test_spaces_returned_dict():
    x = Pymkup(pytest.filename)
    spaces = x.spaces()
    assert 'spaces' in spaces


def test_spaces_returned_dict_vert():
    x = Pymkup(pytest.filename)
    spaces = x.spaces(output='vertices')
    assert type(spaces) == dict


def test_markup_returned_dict():
    x = Pymkup(pytest.filename)
    columns = list(x.get_columns().values())
    columns += Pymkup.extended_columns()
    markup = x.markups(column_list=columns)
    assert 'markups' in markup
