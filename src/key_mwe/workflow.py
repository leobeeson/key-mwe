from collections import Counter
from collections.abc import Iterator


from .ngram_dict_tokeniser import NgramDictTokeniser
from .npmi_estimator import NpmiEstimator
from .keyness_estimator import KeynessEstimator


class StreamedPipeline:

    def __init__(self) -> None:
        pass

    
    def extract_ngram_features(
            self, 
            tokeniser: NgramDictTokeniser, 
            sentences: list[str] | set[str] | Iterator[str]
        ) -> dict[int, list[tuple[str, float]]]:
        ngrams = self.tokenise(tokeniser, sentences)
        npmi_values = self.extract_unigrams_and_collocations(ngrams)
        return npmi_values


    def extract_key_ngram_features(
            self, 
            tokeniser_positive: NgramDictTokeniser, 
            tokeniser_reference: NgramDictTokeniser,
            sentences_positive: list[str] | set[str] | Iterator[str], 
            sentences_reference: list[str] | set[str] | Iterator[str],
        ) -> None:
        ngrams_positive: dict[int, Counter] = self.tokenise(tokeniser_positive, sentences_positive)
        ngrams_reference: dict[int, Counter] = self.tokenise(tokeniser_reference, sentences_reference)
        keyness_values: dict[int, list[tuple[str, float]]] = self.estimate_keyness(ngrams_positive, ngrams_reference)
        return keyness_values
        

    def tokenise(
            self, 
            tokeniser: NgramDictTokeniser, 
            sentences: list[str] | set[str] | Iterator[str]
            ) -> dict[int, Counter]:
        tokeniser.tokenise_corpus_from_iterator(sentences)
        ngrams: dict[int, Counter] = tokeniser.get_ngrams()
        return ngrams
    

    def extract_unigrams_and_collocations(
            self, 
            ngrams: dict[int, Counter]
            ) -> None:
        npmi_estimator = NpmiEstimator(ngrams)
        npmi_estimator.estimate_within_corpus_npmi()
        unigrams_and_collocations: dict[int, list[tuple[str, float]]] = npmi_estimator.get_unigrams_and_collocations(
            threshold_probs_unigrams=0, 
            threshold_npmi_collocations=0
            )
        return unigrams_and_collocations


    def estimate_keyness(
            self, 
            ngrams_positive: dict[int, Counter], 
            ngrams_reference: dict[int, Counter]
            ) -> dict[int, list[tuple[str, float]]]:
        keyness_estimator = KeynessEstimator(ngrams_positive, ngrams_reference)
        keyness_estimator.estimate_cross_corpus_npmi()
        sorted_key_ngrams: dict[int, list[tuple[str, float]]] = keyness_estimator.get_top_ngrams(
            npmi_threshold=0,
            min_freq=3)
        return sorted_key_ngrams
