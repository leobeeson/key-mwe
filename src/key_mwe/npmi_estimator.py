import math
import logging


from collections import Counter


class NpmiEstimator:
    
    LOG_MIN_VALUE = 1e-10
    LOG_MIN = math.log(LOG_MIN_VALUE)
    

    def __init__(self, ngrams: dict[int, Counter]) -> None:
        self.ngrams = ngrams
        self.ngram_probs: dict[int, dict[str, float]] = {n: {} for n in self.ngrams.keys()}
        self.npmi_values: dict[int, dict[str, float]] = {n: {} for n in self.ngrams.keys()}
        self.total_counts = {n: sum(self.ngrams[n].values()) for n in self.ngrams.keys()}
        self.log_probs = {1: {token: math.log(prob) for token, prob in self.ngram_probs[1].items()}}


    def estimate_within_corpus_npmi(self, adjusted: bool = True) -> None:
        for n in self.ngrams.keys():
            for ngram in self.ngrams[n].keys():
                self.estimate_ngram_npmi(n, ngram, adjusted)


    def estimate_ngram_npmi(self, n: int, ngram: str, adjusted: bool) -> None:
        tokens: list[str] = ngram.split()     
        if len(tokens) != n:
            logging.warning(f'Unexpected number of tokens for n-gram: {ngram}')
            return None
        # prob of ngram in corpus
        p_ngram: float = self.get_ngram_prob(n, ngram)
        # prob of tokens in corpus
        if n > 1:
            p_tokens: list[float] = [self.get_ngram_prob(1, token) for token in tokens]
            log_p_ngram = self.safe_log(p_ngram)
            log_p_tokens = [self.safe_log(p) for p in p_tokens]
            # Calculate PMI
            log_prod_p_tokens: float = sum(log_p_tokens)  # log(a*b) = log(a) + log(b)
            pmi: float = log_p_ngram - log_prod_p_tokens  # log(a/b) = log(a) - log(b)
            # Normalizing PMI
            npm: float = pmi / -log_p_ngram
            # Adjusted NPMI Calculation
            if adjusted:
                length_factor = math.log(1 + n)
                freq_factor = math.log(1 + self.ngrams[n][ngram])
                npm = (npm / length_factor) * freq_factor
            # Caching the calculated NPMI value
            self.npmi_values[n][ngram] = npm

    
    def get_ngram_prob(self, n: int, ngram: str) -> float:
        ngrams_n = self.ngrams[n]
        ngram_probs_n = self.ngram_probs[n]
        if ngram not in ngram_probs_n:
            ngram_probs_n[ngram] = ngrams_n[ngram] / self.total_counts[n]
        return ngram_probs_n[ngram]


    def get_npmi_value(self, n: int, ngram: str) -> float | None:
        if ngram not in self.npmi_values[n]:
            self.estimate_ngram_npmi(n, ngram)
        return self.npmi_values[n].get(ngram)
    

    def get_sorted_unigram_probs(self, top_n: int = None, threshold: float = None, reverse: bool = True) -> list[tuple[str, float]]:
        sorted_unigrams: list[tuple[str, float]] = sorted(self.ngram_probs[1].items(), key=lambda item: item[1], reverse=reverse)
        if threshold:
            sorted_unigrams = [item for item in sorted_unigrams if item[1] > threshold]
        if top_n:
            sorted_unigrams = sorted_unigrams[:top_n]
        return sorted_unigrams


    def get_sorted_npmi_values(self, top_n: int = None, threshold: float = None, reverse: bool = True) -> dict[int, list[tuple[str, float]]]:
        sorted_values = {}
        for n, ngram_dict in self.npmi_values.items():
            sorted_values[n] = sorted(ngram_dict.items(), key=lambda item: item[1], reverse=reverse)
            if threshold:
                sorted_values[n] = [item for item in sorted_values[n] if item[1] > threshold]
            if top_n:
                sorted_values[n] = sorted_values[n][:top_n]
        return sorted_values


    @staticmethod
    def safe_log(value: float):
        if value < NpmiEstimator.LOG_MIN_VALUE:
            return NpmiEstimator.LOG_MIN
        return math.log(value)
