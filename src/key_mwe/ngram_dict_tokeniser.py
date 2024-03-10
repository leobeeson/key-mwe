from gensim.models.word2vec import LineSentence
from collections import Counter


class NgramDictTokeniser:

    def __init__(self, mwe_range: list[int], blacklist: list[str] | set[str]) -> None:
        self.n_range: list[int] = [1] + mwe_range
        self.blacklist: list[str] | set[str] = set(blacklist)
        self.ngrams: dict[int, Counter] = {n: Counter() for n in self.n_range}


    def tokenise_corpus_from_text_file(self, corpus_file: str) -> None:
        for sentence in LineSentence(corpus_file):
            self.update_counts(sentence)


    def update_counts(self, sentence: list[str]):
        for n in self.n_range:
            if n == 1:
                self.ngrams[n].update(sentence)
            else:
                ngrams_sentence = [' '.join(sentence[i: i+n]) for i in range(len(sentence) - n + 1)
                                    if sentence[i] not in self.blacklist and sentence[i+n-1] not in self.blacklist]
                self.ngrams[n].update(ngrams_sentence)


    def get_ngrams(self) -> dict[int, Counter]:
        return self.ngrams


    def get_ngram_counts(self, n: int) -> Counter:
        return self.ngrams[n]
