import pytest
from collections import Counter
from src.key_mwe.npmi_estimator import NpmiEstimator

@pytest.fixture
def basic_ngrams() -> dict[int, Counter]:
    return {
        1: Counter({'test': 4, 'example': 2}),
        2: Counter({'test example': 2, 'example test': 1})
    }

@pytest.fixture
def complex_ngrams() -> dict[int, Counter]:
    return {
        1: Counter({'test': 5, 'example': 3, 'sample': 2}),
        2: Counter({'test example': 3, 'example test': 2, 'test sample': 1}),
        3: Counter({'test example sample': 1})
    }

@pytest.fixture
def npmi_estimator_basic(basic_ngrams: dict[int, Counter]) -> NpmiEstimator:
    return NpmiEstimator(basic_ngrams)


@pytest.fixture
def npmi_estimator_complex(complex_ngrams: dict[int, Counter]) -> NpmiEstimator:
    return NpmiEstimator(complex_ngrams)


def test_initialization_basic(npmi_estimator_basic: NpmiEstimator) -> None:
    assert isinstance(npmi_estimator_basic, NpmiEstimator)
    assert npmi_estimator_basic.ngrams == {
        1: Counter({'test': 4, 'example': 2}),
        2: Counter({'test example': 2, 'example test': 1})
    }


def test_initialization_complex(npmi_estimator_complex: NpmiEstimator) -> None:
    assert isinstance(npmi_estimator_complex, NpmiEstimator)
    assert npmi_estimator_complex.ngrams == {
        1: Counter({'test': 5, 'example': 3, 'sample': 2}),
        2: Counter({'test example': 3, 'example test': 2, 'test sample': 1}),
        3: Counter({'test example sample': 1})
    }


def test_estimate_ngram_npmi_basic_estimates_npmi_one_ngram_not_unigram(npmi_estimator_basic: NpmiEstimator) -> None:
    npmi_estimator_basic.estimate_ngram_npmi(2, 'test example', False)
    assert 'test example' in npmi_estimator_basic.npmi_values[2]


def test_estimate_within_corpus_npmi_basic_estimates_npmi_for_all_ngrams_not_unigrams(npmi_estimator_basic: NpmiEstimator) -> None:
    npmi_estimator_basic.estimate_within_corpus_npmi()
    assert all(ngram in npmi_estimator_basic.npmi_values[n] for n in npmi_estimator_basic.ngrams if n > 1 for ngram in npmi_estimator_basic.ngrams[n])


def test_get_ngram_prob_basic(npmi_estimator_basic: NpmiEstimator) -> None:
    prob: float = npmi_estimator_basic.get_ngram_prob(1, 'test')
    assert prob == 4/6


def test_get_sorted_npmi_values_basic_adjusted_true(npmi_estimator_basic: NpmiEstimator) -> None:
    npmi_estimator_basic.estimate_within_corpus_npmi(adjusted=True)
    sorted_values: dict[int, list[tuple[str, float]]] = npmi_estimator_basic.get_sorted_npmi_values()
    assert isinstance(sorted_values, dict)
    assert all(isinstance(sorted_values[n], list) for n in sorted_values)
    top_bigram: tuple[str, float] = sorted_values[2][0]
    top_bigram = (top_bigram[0], round(top_bigram[1], 2))
    assert top_bigram == ("test example", round(2.7095112913514545, 2))


def test_get_sorted_npmi_values_basic_adjusted_false(npmi_estimator_basic: NpmiEstimator) -> None:
    npmi_estimator_basic.estimate_within_corpus_npmi(adjusted=False)
    sorted_values: dict[int, list[tuple[str, float]]] = npmi_estimator_basic.get_sorted_npmi_values()
    assert isinstance(sorted_values, dict)
    assert all(isinstance(sorted_values[n], list) for n in sorted_values)
    top_bigram: tuple[str, float] = sorted_values[2][0]
    top_bigram = (top_bigram[0], round(top_bigram[1], 2))
    assert top_bigram == ("test example", round(2.7095112913514545, 2))


def test_unexpected_ngram_length_basic(npmi_estimator_basic: NpmiEstimator) -> None:
    npmi_estimator_basic.estimate_ngram_npmi(2, 'unexpected bigram', False)
    assert 'this is unexpected' not in npmi_estimator_basic.npmi_values[2]


def test_safe_log_edge_cases(npmi_estimator_basic: NpmiEstimator) -> None:
    assert npmi_estimator_basic.safe_log(NpmiEstimator.LOG_MIN_VALUE) == NpmiEstimator.LOG_MIN
    assert npmi_estimator_basic.safe_log(0) == NpmiEstimator.LOG_MIN
