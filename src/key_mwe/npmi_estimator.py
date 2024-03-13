import math
import logging


from collections import Counter


class NpmiEstimator:
    
    LOG_MIN_VALUE = 1e-10
    LOG_MIN = math.log(LOG_MIN_VALUE)
    

    def __init__(self, ngrams: dict[int, Counter]) -> None:
        self.ngrams: dict[int, Counter] = {n: counter for n, counter in ngrams.items() if counter}
        self.ngram_probs: dict[int, dict[str, float]] = {n: {} for n in self.ngrams.keys()}
        self.npmi_values: dict[int, dict[str, float]] = {n: {} for n in self.ngrams.keys()}
        self.total_counts: dict[int, int] = {n: sum(self.ngrams[n].values()) for n in self.ngrams.keys()}


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
        # If only one ngram in an ngram size, assume an npmi of "neutral":
        if p_ngram == 1:
            self.npmi_values[n][ngram] = 0
            return
        # prob of tokens in corpus
        if n > 1:
            p_tokens: list[float] = [self.get_ngram_prob(1, token) for token in tokens]
            log_p_ngram: float = self.safe_log(p_ngram)
            log_p_tokens: float = [self.safe_log(p) for p in p_tokens]
            # Calculate PMI
            log_prod_p_tokens: float = sum(log_p_tokens)  # log(a*b) = log(a) + log(b)
            pmi: float = log_p_ngram - log_prod_p_tokens  # log(a/b) = log(a) - log(b)
            # Normalizing PMI
            npmi: float = pmi / -log_p_ngram
            # Alternative approach to PMI calculation:
            # prod_p_tokens: float = math.prod(p_tokens)
            # pmi: float = math.log(p_ngram / prod_p_tokens)
            # npmi: float = pmi / -math.log(p_ngram)
            # Adjusted NPMI Calculation
            if adjusted:
                length_factor: float = math.log(1 + n)
                freq_factor: float = math.log(1 + self.ngrams[n][ngram])
                npmi: float = (npmi / length_factor) * freq_factor
            # Caching the calculated NPMI value
            self.npmi_values[n][ngram] = npmi

    
    def get_ngram_prob(self, n: int, ngram: str) -> float:
        if n in self.ngrams.keys():
            ngrams_n: Counter = self.ngrams[n]
            ngram_probs_n: dict[int, dict[str, float]] = self.ngram_probs[n]
            if ngram not in ngram_probs_n:
                ngram_probs_n[ngram] = ngrams_n[ngram] / self.total_counts[n]
            return ngram_probs_n[ngram]
        else:
            return self.LOG_MIN_VALUE


    def get_npmi_value(self, n: int, ngram: str) -> float | None:
        if n in self.ngrams.keys():
            if ngram not in self.npmi_values[n]:
                self.estimate_ngram_npmi(n, ngram)
            return self.npmi_values[n].get(ngram)
        return None
    

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


    def get_unigrams_and_collocations(
            self, 
            top_n_unigrams: int = None, 
            threshold_probs_unigrams: int = None,
            top_n_collocations: int = None, 
            threshold_npmi_collocations: float = None, 
            reverse: bool = True
        ) -> dict[int, list[tuple[str, float]]]:
        sorted_unigrams: list[tuple[str, float]] = self.get_sorted_unigram_probs(
            top_n=top_n_unigrams, 
            threshold=threshold_probs_unigrams, 
            reverse=reverse
            )
        sorted_collocations: dict[int, list[tuple[str, float]]] = self.get_sorted_npmi_values(
            top_n=top_n_collocations, 
            threshold=threshold_npmi_collocations, 
            reverse=reverse
            )
        if len(sorted_unigrams) > 0:
            sorted_collocations[1] = sorted_unigrams
        return sorted_collocations


    @staticmethod
    def safe_log(value: float) -> float:
        if value < NpmiEstimator.LOG_MIN_VALUE:
            return NpmiEstimator.LOG_MIN
        return math.log(value)
