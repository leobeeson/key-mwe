from gensim.models.word2vec import LineSentence
from collections import Counter
from collections.abc import Iterator

from .config import SEPARATOR_TOKEN
from .text_preprocessor import Preprocessor


class NgramDictTokeniser:

    def __init__(self, mwe_range: list[int], blacklist: list[str] | set[str]) -> None:
        self.n_range: list[int] = [1] + mwe_range
        self.blacklist: set[str] = self._set_blacklist(blacklist)
        self.ngrams: dict[int, Counter] = {n: Counter() for n in self.n_range}


    def _set_blacklist(self, blacklist: list[str] | set[str]) -> set[str]:
        blacklist: set[str] = set(blacklist) | {SEPARATOR_TOKEN, SEPARATOR_TOKEN.lower()}
        return blacklist


    def tokenise_corpus_from_text_file(self, corpus_file: str) -> None:
        # Assumption: Text file has had text already preprocessed elsewhere.
        for sentence in LineSentence(corpus_file):
            self.update_counts(sentence)


    def tokenise_corpus_from_iterator(self, sentences: Iterator[str]) -> None:
        preprocessor = Preprocessor()
        for sentence in sentences:
            sentence_processed: str = preprocessor.clean_line(sentence)
            self.update_counts(sentence_processed.split())


    def update_counts(self, sentence: list[str]):
        for n in self.n_range:
            if n == 1:
                self.ngrams[n].update([token for token in sentence if token not in [SEPARATOR_TOKEN, SEPARATOR_TOKEN.lower()]])
            else:
                ngrams_sentence = [' '.join(sentence[i: i+n]) for i in range(len(sentence) - n + 1)
                                    if sentence[i] not in self.blacklist and sentence[i+n-1] not in self.blacklist and SEPARATOR_TOKEN not in sentence[i: i+n] and SEPARATOR_TOKEN.lower() not in sentence[i: i+n]]
                self.ngrams[n].update(ngrams_sentence)


    def get_ngrams(self) -> dict[int, Counter]:
        return self.ngrams


    def get_ngram_counts(self, n: int) -> Counter:
        return self.ngrams[n]
