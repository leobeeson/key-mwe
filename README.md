# key-mwe

[![PyPI - Version](https://img.shields.io/pypi/v/key-mwe.svg)](https://pypi.org/project/key-mwe)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/key-mwe.svg)](https://pypi.org/project/key-mwe)

-----

## Table of Contents

- [key-mwe](#key-mwe)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [License](#license)
  - [Usage](#usage)

## Installation

```console
pip install key-mwe
```

## License

`key-mwe` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Usage

- Provide corpus as one or multiple text files.
- Set up a `NgramDictTokenizer` defining:
  - `mwe_range`: Range of ngrams to count (i.e. bigrams, trigrams, four-grams, etc.) as a `list[int]`.
  - `blacklist`: List of terms to ignore when building ngrams.
- For every text file, run `NgramDictTokenizer.count_unigrams_and_ngrams(corpus_file_path: str)`.
  - Every additional text file updates the ngram counters in `NgramDictTokenizer.ngrams`.
