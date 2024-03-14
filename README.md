# key-mwe

[![PyPI - Version](https://img.shields.io/pypi/v/key-mwe.svg)](https://pypi.org/project/key-mwe)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/key-mwe.svg)](https://pypi.org/project/key-mwe)

-----

## About

- Extracts keywords and multi-word expressions (MWE) using within corpus PMI.
- Estimates keyword and MWE Keyness using between corpora PMI.

## Table of Contents

- [key-mwe](#key-mwe)
  - [About](#about)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [License](#license)
  - [Use Cases](#use-cases)
    - [Inputs](#inputs)
    - [Outputs](#outputs)
  - [Usage](#usage)
    - [Ingestion](#ingestion)
      - [Stream Corpus with Iterable](#stream-corpus-with-iterable)
      - [Read Corpus from Disc](#read-corpus-from-disc)
    - [Ngram Extraction](#ngram-extraction)
      - [Extract Keywords and Collocations](#extract-keywords-and-collocations)
      - [Estimate Keyword and Collocation Keyness](#estimate-keyword-and-collocation-keyness)
  - [Definitions](#definitions)
    - [Keywords](#keywords)
    - [Multi-Word Expression (MWE)](#multi-word-expression-mwe)
      - [Non-Compositional Multi-Word Expression](#non-compositional-multi-word-expression)
      - [Compositional Multi-Word Expression](#compositional-multi-word-expression)
      - [Collocations](#collocations)
      - [Difference between Compositional MWE and Collocations](#difference-between-compositional-mwe-and-collocations)
      - [Difference Between Non-Compositional MWE and Other MWE](#difference-between-non-compositional-mwe-and-other-mwe)

## Installation

```console
pip install key-mwe
```

## License

`key-mwe` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Use Cases

### Inputs

1. Stream corpus' text through an iterable.
2. Read corpus from disc.

### Outputs

1. Extract `keywords` and `collocations` from a corpus.
2. Estimate `keyword` keyness for a given domain.

## Usage

### Ingestion

#### Stream Corpus with Iterable

- Provide corpus as an iterable object.
- Set up a `NgramDictTokenizer` defining:
  - `mwe_range`: Range of ngrams to count (i.e. bigrams, trigrams, four-grams, etc.) as a `list[int]`.
  - `blacklist`: List of terms to ignore when building ngrams.
- Pass the iterable object to `NgramDictTokeniser.tokenise_corpus_from_iterator(sentences: Iterator[str])`
- Every sentence is preprocessed with some basic cleaning done by `Preprocessor.clean_line(sentence)`.

  ```python
  import nltk
  from nltk.corpus import stopwords
  # nltk.download('stopwords')
  from .ngram_dict_tokeniser import NgramDictTokeniser

  blacklist = set(stopwords.words("english"))
  mwe_range: list[int] = [2, 3, 4]
  content: str = "Some long content.\nWith multiple sentences.\nThe more the better."
  sentences: list[str] = [sentence for sentence in content.split('\n') if sentence]
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  tokeniser.tokenise_corpus_from_iterator(sentences)
  ngrams: dict[int, Counter] = tokeniser.get_ngrams()
  ```

#### Read Corpus from Disc

- Provide corpus as one or multiple text files.
- Set up a `NgramDictTokenizer` defining:
  - `mwe_range`: Range of ngrams to count (i.e. bigrams, trigrams, four-grams, etc.) as a `list[int]`.
  - `blacklist`: List of terms to ignore when building ngrams.
- For every text file, run `NgramDictTokeniser.tokenise_corpus_from_text_file(corpus_file_path: str)`.
  - Every additional text file updates the ngram counters in `NgramDictTokenizer.ngrams`.
- Assumption: Text files have had text already preprocessed elsewhere.
  - Text cleaning is an upstream activity, and user has the liberty to preprocess text as necessary for use case.

```python
  import nltk
  from nltk.corpus import stopwords
  # nltk.download('stopwords')
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  
  blacklist = set(stopwords.words("english"))
  mwe_range: list[int] = [2, 3, 4]
  filepath: str = "path/to/file.txt."
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  tokeniser.tokenise_corpus_from_text_file(filepath)
  ngrams: dict[int, Counter] = tokeniser.get_ngrams()
  ```

### Ngram Extraction

#### Extract Keywords and Collocations

To extract high-probability keywords and high PMI collocations:

  ```python
  from key_mwe.npmi_estimator import NpmiEstimator

  ngrams: dict[int, Counter] = tokeniser.get_ngrams() # From `Ingestion` above.
  npmi_estimator = NpmiEstimator(ngrams)
  npmi_estimator.estimate_within_corpus_npmi()
  unigrams_and_collocations: dict[int, list[tuple[str, float]]] = npmi_estimator.get_unigrams_and_collocations(
      threshold_probs_unigrams=0, 
      threshold_npmi_collocations=0
  )
  ```

#### Estimate Keyword and Collocation Keyness

To estimate the keyness of keywords and collocations, you need a reference corpus against which to compare your corpus of interest:

  ```python
  from key_mwe.keyness_estimator import KeynessEstimator

  ngrams: dict[int, Counter] = tokeniser.get_ngrams() # From `Ingestion` above.
  content_reference: list[str] = [
    "Content that is unrelated to your positive corpus.\nUse as many orthogonal domains as possible.",
    "Long content fo domain A.\nWith multiple sentences.\nThe more the better.",
    "Long content fo domain B.\nWith multiple sentences.\nThe more the better.",
    "Long content fo domain C.\nWith multiple sentences.\nThe more the better."
  ]
  sentences_reference: list[str] = [sentence for content in content_reference for sentence in content.split("\n")]
  tokeniser_reference = NgramDictTokeniser(mwe_range, blacklist)
  tokeniser_reference.tokenise_corpus_from_iterator(sentences_reference)
  ngrams_reference: dict[int, Counter] = tokeniser_reference.get_ngrams()
  keyness_estimator = KeynessEstimator(ngrams, ngrams_reference)
  keyness_estimator.estimate_cross_corpus_npmi()
  sorted_key_ngrams: dict[int, list[tuple[str, float]]] = keyness_estimator.get_top_ngrams(
      npmi_threshold=0,
      min_freq=3
  )
  ```

## Definitions

### Keywords

Keywords in Natural Language Understanding (NLU) are terms or phrases that carry significant semantic weight, encapsulating the central ideas or themes of a text. They act as semantic markers, guiding the interpretation towards the intended focal points of the communication. The relevance of keywords is context-dependent, shaped by their surrounding textual environment and the specific situational or thematic framework. They act as dynamic nodes within the semantic network of the text, with their significance defined by how effectively they reflect and reinforce the intended messages and themes. By distilling complex narratives into representative elements, keywords help "reify" the semantic landscape for a given domain, making it more tangible and comprehensible.

### Multi-Word Expression (MWE)

A Multi-Word Expression (MWE) is a sequence of words that, together, convey a meaning that may be different from or more than the sum of their individual meanings. MWEs can be compositional or non-compositional, and their interpretation often depends on the specific context and cultural background. They add nuance and richness to language, but their correct use and understanding require a deep knowledge of the language and its contextual subtleties.

#### Non-Compositional Multi-Word Expression

Non-Compositional MWEs are characterized by their idiomatic meaning, which does not arise predictably from the literal meanings of their components. They often exhibit lexical fixedness, meaning that altering the words or their order typically results in a loss of the idiomatic meaning. These expressions are tied to cultural or linguistic backgrounds, making them particularly challenging for language learners. The non-literal interpretation of non-compositional MWEs sets them apart from other types of MWEs.

They can have unique syntactic and morphological properties and include idioms, proverbial sayings, fixed phrases, and certain types of slang. Examples include "spill the beans" (reveal a secret), "cold feet" (nervousness or hesitation), and "a piece of cake" (something very easy).

#### Compositional Multi-Word Expression

Compositional MWEs are multi-word units where the meaning of the phrase can be deduced from the meanings of its individual components. While each word retains its meaning, together they form a concept that is recognized in the dictionary as a unit. These expressions are systematic and predictable in terms of their linguistic behavior.

Examples include "high school" or "science fiction." The combination of the individual meanings forms a unitary concept that is lexicalised in the language.

#### Collocations

Collocations refer to the habitual juxtaposition of a particular word with another word or words with a frequency greater than chance. They are predictable, and their meaning can be deduced from their parts. However, the key characteristic of collocations is their statistical likelihood of co-occurrence rather than their status as a unitary concept.

Collocations could be considered a subset of compositional MWEs since they are predictable and their meaning can be deduced from their parts. Examples include "blond hair," "heavy rain," or "deeply concerned".

#### Difference between Compositional MWE and Collocations

While both compositional MWEs and collocations involve words that come together to form meaningful combinations, they differ in terms of lexicalisation, fixedness, and flexibility. Compositional MWEs tend to be more unitary and fixed, often becoming entries in the lexicon, whereas collocations are defined by their frequent co-occurrence and flexible usage within language.

Compositional MWEs might exhibit a degree of fixedness or standardization in form (e.g., "high school" is typically not rephrased as "elevated school"). Collocations, while frequent, do not necessarily have this fixedness; their components can often be modified or substituted with synonyms without losing their naturalness (e.g., "severely criticize" vs. "harshly criticize").

Compositional MWEs function as units within certain syntactic or semantic roles, while collocations are more about the habitual pairing of words. The distinction lies in the fact that compositional MWEs form a single lexical item, while collocations are identified based on statistical co-occurrence.

#### Difference Between Non-Compositional MWE and Other MWE

The main difference between non-compositional MWEs and other types of MWEs, such as compositional ones, lies in the predictability of meaning. While compositional MWEs and collocations are generally understandable based on the meanings of their individual components, non-compositional MWEs require knowledge beyond the literal meanings. This non-literal interpretation sets them apart and makes them a unique feature of natural language.
