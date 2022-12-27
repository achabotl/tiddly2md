from typing import Union, List

import pytest

from tiddly2md import list_from_tags, extract_special_tags, add_quotation_marks, unnumbered_lists


@pytest.mark.parametrize("raw, outlist",
[
('[[BaSe Session 14.07.2020: PWR_V3_2 aufgebaut, BPi aufsetzen]] python', ['BaSe Session 14.07.2020: PWR_V3_2 aufgebaut, BPi aufsetzen', 'python']),
('[[BaSe HW rev3b]] BaSe_PWR_V3_2 [[BaSe SBC-Funktionalität]]', ['BaSe HW rev3b', 'BaSe_PWR_V3_2', 'BaSe SBC-Funktionalität']),
('[[BaSe Platinen]]', ['BaSe Platinen']),
('protokoll [[BaSe Protokolle]]', ['protokoll', 'BaSe Protokolle']),
('oneword', ['oneword']),
('oneword anotheroneword', ['oneword', 'anotheroneword']),
(float('nan'), [""]),
]
)
def test_tags(raw: Union[str, float], outlist: List[str]):
    assert set(list_from_tags(raw)) == set(outlist)


@pytest.mark.parametrize("raw, proc", [
    (['a b'], ['"a b"']),
    (['a'], ['a']),
    (['a b', 'ab'], ['"a b"', 'ab'])
])
def test_add_quotation_marks(raw, proc):
    assert add_quotation_marks(raw) == proc


@pytest.mark.parametrize("tags, frontmatter", [(
    ['c'], '---\nup: c\nprogrammiersprache: c\n---\n\n'
)])
def test_extract_special_tags(tags: List[str], frontmatter: str):
    assert extract_special_tags(tags) == frontmatter


@pytest.mark.parametrize("tid_list, md_list", [
    ("* list item1", "- list item1"),
    ("*list item1", "- list item1"),
    ("**list item2", "  - list item2")
])
def test_unnumbered_lists(tid_list: str, md_list: str):
    assert unnumbered_lists(tid_list) == md_list