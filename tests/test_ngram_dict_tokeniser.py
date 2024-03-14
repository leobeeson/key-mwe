import pytest
from unittest.mock import patch
from collections import Counter


from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser


@pytest.fixture
def sample_blacklist() -> list[str]:
    return ['a', 'an', 'the']


@pytest.fixture
def sample_mwe_range() -> list[int]:
    return [2, 3]


@pytest.fixture
def ngram_dict_tokeniser(sample_mwe_range: list[int], sample_blacklist: list[str]) -> NgramDictTokeniser:
    return NgramDictTokeniser(sample_mwe_range, sample_blacklist)


def test_update_counts(ngram_dict_tokeniser: NgramDictTokeniser):
    sentence = ["This", "is", "a", "test", "sentence"]
    ngram_dict_tokeniser.update_counts(sentence)
    expected = {
        1: Counter({"This": 1, "is": 1, "test": 1, "sentence": 1}),  # 'a' is in blacklist
        2: Counter({"This is": 1, "test sentence": 1}),  # 'a' and 'is a' are affected by blacklist
        3: Counter({"This is test": 1})  # Only one valid 3-gram without blacklist words
    }
    assert ngram_dict_tokeniser.get_ngrams() == expected


@pytest.mark.parametrize("corpus, expected", [
    (["This", "is", "a", "test"], {1: Counter({'This': 1, 'is': 1, 'a': 1, 'test': 1}), 
                                   2: Counter({"This is": 1}),
                                   3: Counter({"is a test": 1})}),
    ([], {1: Counter(), 2: Counter(), 3: Counter()}),  # Testing with empty input
    (["This", "is", "another", "test"], {1: Counter({"This": 1, "is": 1, "another": 1, "test": 1}),
                                         2: Counter({'This is': 1, 'is another': 1, 'another test': 1}),
                                         3: Counter({'This is another': 1, 'is another test': 1})}),
    (["With", "two", "sentences"], {1: Counter({"With": 1, "two": 1, "sentences": 1}),
                                    2: Counter({"With two": 1, "two sentences": 1}),
                                    3: Counter({"With two sentences": 1})}),
    (["hello", "zuluzulu", "world", "zuluzulu", "zuluzulu", "cómo", "están", "zuluzulu", "numbers", "zuluzulu", "1234", "zuluzulu"],
     {1: Counter({"hello": 1, "world": 1, "cómo": 1, "están": 1, "numbers": 1, "1234": 1}),
        2: Counter({"cómo están": 1}),
        3: Counter({})})
])
def test_update_counts(ngram_dict_tokeniser: NgramDictTokeniser, corpus: list[list[str]], expected: dict[int, Counter]):
    ngram_dict_tokeniser.update_counts(corpus)
    assert ngram_dict_tokeniser.get_ngrams() == expected


def test_get_ngram_counts(ngram_dict_tokeniser: NgramDictTokeniser):
    # Directly setting the ngrams attribute to test get_ngram_counts
    ngram_dict_tokeniser.ngrams = {1: Counter({'test': 3, 'dummy': 1}), 2: Counter({'test dummy': 2})}
    assert ngram_dict_tokeniser.get_ngram_counts(1) == Counter({'test': 3, 'dummy': 1})
    assert ngram_dict_tokeniser.get_ngram_counts(2) == Counter({'test dummy': 2})
    with pytest.raises(KeyError):
        ngram_dict_tokeniser.get_ngram_counts(3)  # Test for non-existent key
