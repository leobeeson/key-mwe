import pytest
from collections import Counter


from key_mwe.npmi_estimator import NpmiEstimator


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


def test_get_sorted_unigram_probs_no_params(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    sorted_unigrams = npmi_estimator_complex.get_sorted_unigram_probs()
    assert sorted_unigrams == [('test', 0.5), ('example', 0.3), ('sample', 0.2)], "Unigrams should be sorted by probability in descending order."


def test_get_npmi_value_single_ngram_in_ngram_size_returns_zero(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    npmi_value = npmi_estimator_complex.get_npmi_value(3, 'test example sample')
    assert npmi_value == 0, "NPMI value should be zero for a single ngram in an ngram size."


def test_get_sorted_unigram_probs_with_threshold(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    sorted_unigrams = npmi_estimator_complex.get_sorted_unigram_probs(threshold=0.2)
    assert sorted_unigrams == [('test', 0.5), ('example', 0.3)], "Unigrams should be filtered by a probability greater than the threshold."


def test_get_sorted_unigram_probs_with_top_n(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    sorted_unigrams = npmi_estimator_complex.get_sorted_unigram_probs(top_n=2)
    assert sorted_unigrams == [('test', 0.5), ('example', 0.3)], "Only the top N unigrams should be returned."


def test_get_sorted_unigram_probs_with_reverse(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    sorted_unigrams = npmi_estimator_complex.get_sorted_unigram_probs(reverse=False)
    assert sorted_unigrams == [('sample', 0.2), ('example', 0.3), ('test', 0.5)], "Unigrams should be sorted by probability in ascending order when reverse is False."


def test_get_sorted_npmi_values_no_params(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi(adjusted=True)
    sorted_npmi = npmi_estimator_complex.get_sorted_npmi_values()
    # There should not be npmi values for unigrams:
    assert len(sorted_npmi[1]) == 0
    # Round the NPMI values to 2 decimal places for safe comparison:
    bigram_npmi = sorted_npmi[2]
    bigram_npmi = [(item[0], round(item[1], 2)) for item in bigram_npmi]
    assert bigram_npmi == [('test example', round(2.1918065485787688, 2)), ('example test', round(0.7268330278608419, 2)), ('test sample', round(0.17987631177945834, 2))]
    # Since there is only one trigram, it's npmi was assumed to be zero (neutral):
    trigram_npmi = sorted_npmi[3]
    assert trigram_npmi == [('test example sample', 0)]


def test_get_sorted_npmi_values_with_threshold(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    threshold = 0.5
    sorted_npmi = npmi_estimator_complex.get_sorted_npmi_values(threshold=threshold)
    # We can only test the bigram NPMI values since the trigram NPMI value is zero, and unigrams are not included:
    bigram_npmi = sorted_npmi[2]
    bigram_npmi = [(item[0], round(item[1], 2)) for item in bigram_npmi]
    assert bigram_npmi == [('test example', round(2.1918065485787688, 2)), ('example test', round(0.7268330278608419, 2))]
    # Test that all NPMI values are greater than the threshold:
    assert all(item[1] > threshold for npmi_list in sorted_npmi.values() for item in npmi_list), "All NPMI values should be greater than the threshold."


def test_get_sorted_npmi_values_with_top_n(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    top_n = 1
    sorted_npmi = npmi_estimator_complex.get_sorted_npmi_values(top_n=top_n)
    # Since unigrams is empty, we can only test bigram and trigram NPMI values:
    bigram_npmi = sorted_npmi[2]
    bigram_npmi = [(item[0], round(item[1], 2)) for item in bigram_npmi]
    assert bigram_npmi == [('test example', round(2.1918065485787688, 2))]
    trigram_npmi = sorted_npmi[3]
    assert trigram_npmi == [('test example sample', 0)]
    assert all(len(npmi_list) <= top_n for n, npmi_list in sorted_npmi.items() if n > 1), "Only the top N NPMI values should be returned for each n."


def test_get_sorted_npmi_values_with_reverse(npmi_estimator_complex: NpmiEstimator) -> None:
    npmi_estimator_complex.estimate_within_corpus_npmi()
    sorted_npmi = npmi_estimator_complex.get_sorted_npmi_values(reverse=False)
    # Since unigrams is empty, we can only test bigram and trigram NPMI values:
    bigram_npmi = sorted_npmi[2]
    bigram_npmi = [(item[0], round(item[1], 2)) for item in bigram_npmi]
    assert bigram_npmi == [('test sample', round(0.17987631177945834, 2)), ('example test', round(0.7268330278608419, 2)), ('test example', round(2.1918065485787688, 2))]
    trigram_npmi = sorted_npmi[3]
    assert trigram_npmi == [('test example sample', 0)]
