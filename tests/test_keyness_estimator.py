import pytest
from collections import Counter


from key_mwe.bespoke_types import keyness
from key_mwe.keyness_estimator import KeynessEstimator


@pytest.fixture
def positive_ngrams() -> dict[int, Counter]:
    return {
        1: Counter({'data': 15, 'analysis': 10, 'model': 8, 'algorithm': 5, 'language': 3}),
        2: Counter({'data analysis': 9, 'predictive model': 5, 'language model': 4, 'analysis algorithm': 3}),
        3: Counter({'big data analysis': 3, 'predictive model accuracy': 2})
    }


@pytest.fixture
def reference_ngrams() -> dict[int, Counter]:
    return {
        1: Counter({'language': 18, 'syntax': 12, 'phonetics': 9, 'model': 7, 'data': 5}),
        2: Counter({'sentence structure': 8, 'phonetic variation': 5, 'language model': 4, 'data analysis': 3}),
        3: Counter({'universal grammar theory': 4, 'lexical functional grammar': 2})
    }


@pytest.fixture
def keyness_estimator(positive_ngrams: dict[int, Counter], reference_ngrams: dict[int, Counter]) -> KeynessEstimator:
    return KeynessEstimator(positive_ngrams, reference_ngrams)


def test_keyness_estimator_initialization(keyness_estimator: KeynessEstimator) -> None:
    assert isinstance(keyness_estimator.ngrams, dict)
    assert isinstance(keyness_estimator.ngrams_reference, dict)
    assert 1 in keyness_estimator.ngrams and 1 in keyness_estimator.ngrams_reference, "Both positive and reference should have unigrams."
    assert 2 in keyness_estimator.ngrams and 2 in keyness_estimator.ngrams_reference, "Both positive and reference should have bigrams."
    assert 3 in keyness_estimator.ngrams and 3 in keyness_estimator.ngrams_reference, "Both positive and reference should have trigrams."
    assert keyness_estimator.total_counts[1] == 41
    assert keyness_estimator.total_counts[2] == 21
    assert keyness_estimator.total_counts[3] == 5
    assert keyness_estimator.total_counts_ref[1] == 51
    assert keyness_estimator.total_counts_ref[2] == 20
    assert keyness_estimator.total_counts_ref[3] == 6


def test_keyness_estimator_accurately_calculates_cross_corpus_npmi(keyness_estimator: KeynessEstimator) -> None:
    keyness_estimator.estimate_cross_corpus_npmi(adjusted=False)
    assert 'data analysis' in keyness_estimator.keyness_values[2], "NPMI values should include 'data analysis' for bigrams."       
    # Verify that common terms have NPMI values calculated and that they make sense relative to the corpus
    common_terms = ['data', 'model', 'language']  # Common terms expected to be in both corpora
    for term in common_terms:
        if term in keyness_estimator.ngrams[1]:
            assert term in keyness_estimator.keyness_values[1], f"NPMI values should include the term '{term}' for unigrams."
    # Check for non-zero NPMI values for at least some overlapping n-grams, npmi estimation is being executed correctly
    overlapping_ngrams = set(keyness_estimator.ngrams[2]) & set(keyness_estimator.ngrams_reference[2])
    non_zero_npmi = [ngram for ngram in overlapping_ngrams if keyness_estimator.keyness_values[2].get(ngram, 0) != 0]
    assert non_zero_npmi, "There should be non-zero NPMI values for overlapping bigrams, indicating a meaningful cross-corpus comparison."


def test_get_ngram_prob_from_ref_corpus(keyness_estimator: KeynessEstimator) -> None:
    prob = keyness_estimator.get_ngram_prob_ref(1, 'language')
    assert prob > KeynessEstimator.LOG_MIN_VALUE, "'language' should have a positive probability in the reference corpus."


def test_get_top_ngrams_by_keyness(keyness_estimator: KeynessEstimator) -> None:
    keyness_estimator.estimate_cross_corpus_npmi()
    top_ngrams = keyness_estimator.get_top_ngrams(top_k=5, min_freq=5)
    assert "positive" in top_ngrams, "There should be a 'positive' category in the top n-grams."
    assert 3 not in top_ngrams["positive"], "There should be no trigrams in the top n-grams because all trigrams violate the `min_freq: int = 5` parameter."
    assert all(len(top_ngrams['positive'][n]) <= 5 for n in top_ngrams['positive']), "Each n in 'positive' should have at most 5 top n-grams."


def test_get_top_ngrams_with_threshold(keyness_estimator: KeynessEstimator) -> None:
    keyness_estimator.estimate_cross_corpus_npmi()
    threshold = 0.1
    top_ngrams: keyness = keyness_estimator.get_top_ngrams(npmi_threshold=threshold)
    assert all(value[3] >= threshold for ngram_list in top_ngrams['positive'].values() for value in ngram_list), "All top n-grams should meet the NPMI threshold."


def test_get_top_ngrams_symmetric(keyness_estimator: KeynessEstimator) -> None:
    keyness_estimator.estimate_cross_corpus_npmi()
    top_ngrams = keyness_estimator.get_top_ngrams(top_k=3, symmetric=True)
    assert 'negative' in top_ngrams, "Symmetric top n-grams should include 'negative' category."
    assert all(len(top_ngrams['negative'][n]) <= 3 for n in top_ngrams['negative']), "Each n in 'negative' should have at most 3 top n-grams."
