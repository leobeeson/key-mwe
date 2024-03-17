


corpus_type_str = str
ngram_str = str
ngram_size_int = int
freq_target_int = int
freq_reference_int = int
keyness_value_float = float


keyness = dict[corpus_type_str, dict[ngram_size_int, list[tuple[ngram_str, freq_target_int, freq_reference_int, keyness_value_float]]]]
