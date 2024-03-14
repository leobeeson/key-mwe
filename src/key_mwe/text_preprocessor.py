import re
import string


from collections.abc import Callable
from gensim.parsing.preprocessing import (
    strip_tags, 
    strip_multiple_whitespaces
)


from .config import SEPARATOR_TOKEN


class Preprocessor:


    def __init__(self) -> None:
        self.custom_filters: list[Callable[[str], str]] = [
            strip_tags,
            self.custom_strip_punctuation,
            self.custom_strip_non_alphanumeric,
            strip_multiple_whitespaces
        ]

    
    def custom_strip_punctuation(self, sentence: str) -> str:
        spanish_punctuation: str = string.punctuation + '¡¿'
        RE_PUNCT: re.Pattern = re.compile(r'([%s])+' % re.escape(spanish_punctuation), re.UNICODE)
        replacement: str = f" {SEPARATOR_TOKEN} "
        return RE_PUNCT.sub(replacement, sentence)


    def custom_strip_non_alphanumeric(self, sentence: str) -> str:
        RE_NONALPHA = re.compile(r"[^\wáéíóúüñÁÉÍÓÚÜÑ]+", re.UNICODE)
        return RE_NONALPHA.sub(" ", sentence)


    def clean_line(self, sentence: str, lower_case: bool = True) -> str:
        for filter in self.custom_filters:
            sentence: str = filter(sentence)
        if lower_case:
            sentence: str = sentence.lower()
        return sentence.strip()
