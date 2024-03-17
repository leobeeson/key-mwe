from collections import Counter
from collections.abc import Iterator


from .bespoke_types import keyness
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
        ngrams_counts = self.tokenise(tokeniser, sentences)
        ngrams_filtered = self.extract_unigrams_and_collocations(ngrams_counts)
        return ngrams_filtered


    def extract_key_ngram_features(
            self, 
            tokeniser_positive: NgramDictTokeniser, 
            tokeniser_reference: NgramDictTokeniser,
            sentences_positive: list[str] | set[str] | Iterator[str], 
            sentences_reference: list[str] | set[str] | Iterator[str],
            top_k: int | None = None, 
            npmi_threshold: float | None = 0.0, 
            min_freq_target: int = 3,
            symmetric: bool = False,
        ) -> keyness:
        ngrams_positive: dict[int, Counter] = self.tokenise(tokeniser_positive, sentences_positive)
        ngrams_reference: dict[int, Counter] = self.tokenise(tokeniser_reference, sentences_reference)
        keyness_values: keyness = self.estimate_keyness(ngrams_positive, ngrams_reference, top_k, npmi_threshold, min_freq_target, symmetric)
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
            ) -> dict[int, list[tuple[str, float]]]:
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
            ngrams_reference: dict[int, Counter],
            top_k: int | None = None, 
            npmi_threshold: float | None = None, 
            min_freq_target: int = 3,
            symmetric: bool = False,
            ) -> keyness:
        keyness_estimator = KeynessEstimator(ngrams_positive, ngrams_reference)
        keyness_estimator.estimate_cross_corpus_npmi()
        sorted_key_ngrams: keyness = keyness_estimator.get_top_ngrams(
            top_k=top_k,
            npmi_threshold=npmi_threshold,
            min_freq=min_freq_target,
            symmetric=symmetric)
        return sorted_key_ngrams
