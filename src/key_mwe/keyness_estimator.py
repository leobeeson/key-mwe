import math
import logging


from collections import Counter


from .bespoke_types import keyness
from .npmi_estimator import NpmiEstimator


class KeynessEstimator(NpmiEstimator):
    
    def __init__(self, ngrams_positive: dict[int, Counter], ngrams_reference: dict[int, Counter]) -> None:
        super().__init__(ngrams_positive)
        self.ngrams_reference: dict[int, Counter] = {n: counter for n, counter in ngrams_reference.items() if counter}
        self.total_counts_ref: dict[int, int] = {n: sum(self.ngrams_reference[n].values()) for n in self.ngrams_reference.keys()}
        self.keyness_values: dict[int, dict[str, float]] = {n: {} for n in ngrams_positive.keys()}


    def estimate_cross_corpus_npmi(self, adjusted: bool = True) -> None:
        for n in self.ngrams.keys():
            for ngram in self.ngrams[n].keys():
                self.estimate_keyness(n, ngram, adjusted)
                


    def estimate_keyness(self, n: int, ngram: str, adjusted: bool) -> float:
        tokens: list[str] = ngram.split()
        if len(tokens) != n:
            logging.warning(f'Unexpected number of tokens for n-gram: {ngram}')
            return None
        p_ngram_pos: float = self.get_ngram_prob(n, ngram)
        p_ngram_ref: float = self.get_ngram_prob_ref(n, ngram)
        log_p_ngram_pos: float = self.safe_log(p_ngram_pos)
        log_p_ngram_ref: float = self.safe_log(p_ngram_ref)
        pmi_cross: float = log_p_ngram_pos - log_p_ngram_ref
        # Normalize
        npmi_cross: float = pmi_cross / -log_p_ngram_pos
        # Adjusted NPMI Calculation
        if adjusted:
            length_factor: float = math.log(1 + n)
            freq_factor: float = math.log(1 + self.ngrams[n][ngram])
            npmi_cross: float = (npmi_cross / length_factor) * freq_factor
        self.keyness_values[n][ngram] = npmi_cross


    def get_ngram_prob_ref(self, n: int, ngram: str) -> float:
        if n in self.ngrams_reference.keys():
            ngram_count = self.ngrams_reference[n].get(ngram, self.LOG_MIN_VALUE)
            return ngram_count / self.total_counts_ref[n]
        else:
            return self.LOG_MIN_VALUE


    def get_top_ngrams(self, top_k: int | None = None, npmi_threshold: float | None = None, min_freq: int = 3, symmetric: bool = False) -> keyness:
        """
        Retrieve top n-grams based on either k or npmi_threshold.
        
        :param k: Number of top n-grams to return.
        :param npmi_threshold: NPMI threshold value.
        :param symmetric: If True, returns symmetric top k or n for both positive and reference corpus.
        :return: Nested dictionary of top n-grams.
        """
        if top_k is None and npmi_threshold is None:
            raise ValueError("Either top_k or npmi_threshold must be provided.")

        all_ngrams: list[tuple[str, int, int, int, float]] = []
        for n, values in self.keyness_values.items():
            for ngram, value in values.items():
                ngram_frequency_target: int = self.ngrams[n][ngram]
                if ngram_frequency_target >= min_freq:
                    ngram_frequency_reference: int = self.ngrams_reference[n].get(ngram, 0)
                    all_ngrams.append((ngram, n, ngram_frequency_target, ngram_frequency_reference, value))



        all_ngrams.sort(key=lambda x: x[4], reverse=True)

        top_ngrams_response: keyness = {"positive": {}}

        if top_k:
            for ngram, n, freq_target, freq_ref, value in all_ngrams[:top_k]:
                if n not in top_ngrams_response["positive"]:
                    top_ngrams_response["positive"][n] = []
                top_ngrams_response["positive"][n].append((ngram, freq_target, freq_ref, value))
            
            if symmetric:
                top_ngrams_response["negative"] = {}
                for ngram, n, freq_target, freq_ref, value in all_ngrams[-top_k:]:
                    if n not in top_ngrams_response["negative"]:
                        top_ngrams_response["negative"][n] = []
                    top_ngrams_response["negative"][n].append((ngram, freq_target, freq_ref, value))

        elif npmi_threshold is not None:
            for ngram, n, freq_target, freq_ref, value in all_ngrams:
                if value >= npmi_threshold:
                    if n not in top_ngrams_response["positive"]:
                        top_ngrams_response["positive"][n] = []
                    top_ngrams_response["positive"][n].append((ngram, freq_target, freq_ref, value))
                
            if symmetric:
                top_ngrams_response["negative"] = {}
                for ngram, n, freq_target, freq_ref, value in all_ngrams:
                    if value <= -npmi_threshold:
                        if n not in top_ngrams_response["negative"]:
                            top_ngrams_response["negative"][n] = []
                        top_ngrams_response["negative"][n].append((ngram, freq_target, freq_ref, value))


        return top_ngrams_response
