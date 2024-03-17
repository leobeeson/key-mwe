# key-mwe

[![PyPI - Version](https://img.shields.io/pypi/v/key-mwe.svg)](https://pypi.org/project/key-mwe)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/key-mwe.svg)](https://pypi.org/project/key-mwe)

-----

## About

- Extracts keywords and Multi-Word Expressions (MWE) using within corpus PMI.
- Estimates keyword and MWE Keyness using between corpora PMI.
  - Requires a negative or `reference corpus` against which to identify feature keyness in a positive or `target corpus`.

## Caveats

- When extracting ngrams with `npmi_estimator.get_unigrams_and_collocations()`, the values for unigrams are simply occurrence probability (i.e. frequency / total unigrams count).
- When extracting ngrams with `npmi_estimator.get_unigrams_and_collocations()`, MWE npmi values are not normalised between -1 and 1 for several reasons:
  - Heuristics for handling logs of zero-probability ngrams.
  - `length_factor` adjustment scales npmi by ngram size, boosting large ngram-size MWE.
  - `freq_factor` adjustment scales npmi by ngram frequency, boosting more frequent unigrams and MWE in the `target corpus`.

## Table of Contents

- [key-mwe](#key-mwe)
  - [About](#about)
  - [Caveats](#caveats)
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
      - [Extract Keywords and MWE](#extract-keywords-and-mwe)
      - [Estimate Keyword and MWE Keyness](#estimate-keyword-and-mwe-keyness)
      - [Estimate Keyword and MWE Keyness with Negative Features](#estimate-keyword-and-mwe-keyness-with-negative-features)
    - [Streamlined Workflow](#streamlined-workflow)
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

1. Extract `keywords` and `MWE` from a corpus.
2. Estimate `keyword` and `MWE` keyness for a given domain (i.e. `target corpus`).

## Usage

### Ingestion

#### Stream Corpus with Iterable

- Provide corpus as an iterable object.
- Set up a `NgramDictTokenizer` defining:
  - `mwe_range`:
    - Range of ngrams to count (i.e. bigrams, trigrams, four-grams, etc.) as a `list[int]`.
  - `blacklist`:
    - List of terms to ignore when building ngrams.
    - For demonstration, we use the basic `stopwords` list form `nltk`, but we encourage experimenting with:
      - Only pronouns.
      - Only pronouns and prepositions.
      - Blacklisting numbers (as digits and/or string representations, e.g. "two").
      - Blacklisting ambiguous words.
      - Blacklisting domain-specific unigrams.
- Pass the iterable object to `NgramDictTokeniser.tokenise_corpus_from_iterator(sentences: Iterator[str])`
- Every sentence is preprocessed with some basic cleaning done by `Preprocessor.clean_line(sentence)`.

  ```python
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  from collections import Counter
  import nltk
  # nltk.download('stopwords')
  from nltk.corpus import stopwords

  blacklist = set(stopwords.words("english")) # Or define your own use case-specific blacklist.
  mwe_range: list[int] = [2, 3, 4]
  content: str = "Some long content relevant to your target corpus.\nWith multiple sentences relevant to your target corpus.\nThe more target corpus relevant material, the better."
  sentences: list[str] = [sentence for sentence in content.split('\n') if sentence]
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  tokeniser.tokenise_corpus_from_iterator(sentences)
  ngrams: dict[int, Counter] = tokeniser.get_ngrams()
  from pprint import pprint
  pprint(ngrams)
  ```

  ```python
  {
    1: Counter({'relevant': 3,
                'target': 3,
                'corpus': 3,
                'to': 2,
                'your': 2,
                'the': 2,
                'some': 1,
                'long': 1,
                'content': 1,
                'with': 1,
                'multiple': 1,
                'sentences': 1,
                'more': 1,
                'material': 1,
                'better': 1}),
    2: Counter({'target corpus': 3,
                'long content': 1,
                'content relevant': 1,
                'multiple sentences': 1,
                'sentences relevant': 1,
                'corpus relevant': 1,
                'relevant material': 1}),
    3: Counter({'long content relevant': 1,
                'multiple sentences relevant': 1,
                'target corpus relevant': 1,
                'corpus relevant material': 1}),
    4: Counter({'relevant to your target': 2,
                'target corpus relevant material': 1})
  }
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
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  import nltk
  # nltk.download('stopwords')
  from nltk.corpus import stopwords
  
  blacklist = set(stopwords.words("english")) # Or define your own use case-specific blacklist.
  mwe_range: list[int] = [2, 3, 4]
  filepath: str = "path/to/file.txt."
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  tokeniser.tokenise_corpus_from_text_file(filepath)
  ngrams: dict[int, Counter] = tokeniser.get_ngrams()
  print(ngrams)
  ```

### Ngram Extraction

#### Extract Keywords and MWE

To extract high-probability keywords and high PMI MWE:

  ```python
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  from key_mwe.npmi_estimator import NpmiEstimator
  from nltk.corpus import stopwords
  from collections import Counter
  
  blacklist = set(stopwords.words("english"))
  mwe_range: list[int] = [2, 3, 4]
  content: str = "Some long content relevant to your target corpus.\nWith multiple sentences relevant to your target corpus.\nThe more target corpus relevant material, the better."
  sentences: list[str] = [sentence for sentence in content.split('\n') if sentence]
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  tokeniser.tokenise_corpus_from_iterator(sentences)
  ngrams: dict[int, Counter] = tokeniser.get_ngrams()
  npmi_estimator = NpmiEstimator(ngrams)
  npmi_estimator.estimate_within_corpus_npmi()
  unigrams_and_collocations: dict[int, list[tuple[str, float]]] = npmi_estimator.get_unigrams_and_collocations(
      threshold_probs_unigrams=0, 
      threshold_npmi_collocations=0
  )
  from pprint import pprint
  pprint(unigrams_and_collocations)
  ```

  ```python
  {
    1: [('relevant', 0.125),
        ('target', 0.125),
        ('corpus', 0.125),
        ('to', 0.08333333333333333),
        ('your', 0.08333333333333333),
        ('the', 0.08333333333333333),
        ('some', 0.041666666666666664),
        ('long', 0.041666666666666664),
        ('content', 0.041666666666666664),
        ('with', 0.041666666666666664),
        ('multiple', 0.041666666666666664),
        ('sentences', 0.041666666666666664),
        ('more', 0.041666666666666664),
        ('material', 0.041666666666666664),
        ('better', 0.041666666666666664)],
    2: [('target corpus', 3.5150087401579637),
        ('long content', 1.19421706182522),
        ('multiple sentences', 1.19421706182522),
        ('content relevant', 0.8787521850394912),
        ('sentences relevant', 0.8787521850394912),
        ('relevant material', 0.8787521850394912),
        ('corpus relevant', 0.5632873082537624)],
    3: [('long content relevant', 2.542481250360578),
        ('multiple sentences relevant', 2.542481250360578),
        ('corpus relevant material', 2.146240625180289),
        ('target corpus relevant', 1.7499999999999996)],
    4: [('relevant to your target', 14.685682158728854),
        ('target corpus relevant material', 3.2607198558509918)]
  }
  ```

#### Estimate Keyword and MWE Keyness

To estimate the keyness of keywords and MWE, you need a reference corpus against which to compare your corpus of interest:

  ```python
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  from key_mwe.npmi_estimator import NpmiEstimator
  from key_mwe.keyness_estimator import KeynessEstimator
  from key_mwe.bespoke_types import keyness
  from nltk.corpus import stopwords
  from collections import Counter
  
  blacklist = set(stopwords.words("english"))
  mwe_range: list[int] = [2, 3, 4]
  content: str = "Some long content relevant to your target corpus.\nWith multiple sentences relevant to your target corpus.\nThe more target corpus relevant material, the better."
  sentences: list[str] = [sentence for sentence in content.split('\n') if sentence]
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  tokeniser.tokenise_corpus_from_iterator(sentences)
  ngrams_target: dict[int, Counter] = tokeniser.get_ngrams()
  
  content_reference: list[str] = [
    "Content that is unrelated to your target corpus.\nUse as many orthogonal domains as possible.",
    "Long content for domain A, as part of your reference corpus.\nWith multiple sentences.\nThe more the better.",
    "Long content for domain B, as part of your reference corpus.\nWith multiple sentences.\nThe more the better.",
    "Long content for domain C, as part of your reference corpus.\nWith multiple sentences.\nThe more the better."
  ]
  sentences_reference: list[str] = [sentence for content in content_reference for sentence in content.split("\n")]
  tokeniser_reference = NgramDictTokeniser(mwe_range, blacklist)
  tokeniser_reference.tokenise_corpus_from_iterator(sentences_reference)
  ngrams_reference: dict[int, Counter] = tokeniser_reference.get_ngrams()
  keyness_estimator = KeynessEstimator(ngrams_target, ngrams_reference)
  keyness_estimator.estimate_cross_corpus_npmi()
  sorted_key_ngrams: keyness = keyness_estimator.get_top_ngrams(
      npmi_threshold=0,
      min_freq=3
  )
  from pprint import pprint
  pprint(sorted_key_ngrams)
  ```

  ```python
  {'positive': {
                1: [('relevant', 3, 0, 20.146187299249085),
                    ('target', 3, 1, 2.0723496378521133),
                    ('corpus', 3, 4, 0.7390163045187798)],
                2: [('target corpus', 3, 1, 1.769345965087366)]
               }
  }
  ```

  The `keyness` type is defined as following in `.bespoke_types.py`:

  ```python
  corpus_type_str = str
  ngram_str = str
  ngram_size_int = int
  freq_target_int = int
  freq_reference_int = int
  keyness_value_float = float
  keyness = dict[corpus_type_str, dict[ngram_size_int, list[tuple[ngram_str, freq_target_int, freq_reference_int, keyness_value_float]]]]
  ```

  The keyness object can contain two root keys:
    - `positive`:
      - Will always be present, and represent the features in the target corpus that meet the filtering criteria, i.e. `npmi_threshold`, `top_k`, `min_freq`.
    - `reference`:
      - Only present if `symmetric = True` is passed to `keyness_estimator.get_top_ngrams()`, returning the features with the lowest keyness towards the target domain.
      - It uses the same filtering criteria for `positive`, i.e. `npmi_threshold`, `top_k`, `min_freq`, but `npmi_threshold` and `top_k` are negative in order to capture the opposite side of the keyness spectrum (i.e. inverse keyness).
      - **IMPORTANT**: The `negative` features only includes ngrams that exist in the target corpus, not the ngrams with the highest keyness for the reference domain.
      - To estimate `reference` features with highest keyness, swap target corpus for reference corpus, and vice-versa.
      - The `reference` features with highest keyness are useful for using as features with the highest negative signal (i.e. not "neutral") for the target domain, i.e. their presence 

  Within each `corpus_type`, i.e. `positive` or `reference`, there is an object where the keys are the ngram size, containing a list of tuples composed of the following elements:
    - `[0]`: The ngram string (i.e. keyword or multi-word expression).
    - `[1]`: The frequency count of the ngram string in the **target** corpus.
    - `[2]`: The frequency count of the ngram string in the **reference** corpus.
    - `[3]`: The keyness value for the ngram string in the **target** corpus vis-a-vis the **reference** corpus.

#### Estimate Keyword and MWE Keyness with Negative Features

Pass `symmetric = True` to `keyness_estimator.get_top_ngrams()` in order to get the features with the highest negative signal (i.e. inverse keyness) for the target domain:

  ```python
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  from key_mwe.npmi_estimator import NpmiEstimator
  from key_mwe.keyness_estimator import KeynessEstimator
  from key_mwe.bespoke_types import keyness
  from nltk.corpus import stopwords
  from collections import Counter
  
  blacklist = set(stopwords.words("english"))
  mwe_range: list[int] = [2, 3, 4]
  content: str = "Some long content relevant to your target corpus.\nWith multiple sentences relevant to your target corpus.\nThe more target corpus relevant material, the better."
  sentences: list[str] = [sentence for sentence in content.split('\n') if sentence]
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  tokeniser.tokenise_corpus_from_iterator(sentences)
  ngrams_target: dict[int, Counter] = tokeniser.get_ngrams()
  
  content_reference: list[str] = [
    "Content that is unrelated to your target corpus.\nUse as many orthogonal domains as possible.",
    "Long content for domain A, as part of your reference corpus.\nWith multiple sentences.\nThe more the better.",
    "Long content for domain B, as part of your reference corpus.\nWith multiple sentences.\nThe more the better.",
    "Long content for domain C, as part of your reference corpus.\nWith multiple sentences.\nThe more the better."
  ]
  sentences_reference: list[str] = [sentence for content in content_reference for sentence in content.split("\n")]
  tokeniser_reference = NgramDictTokeniser(mwe_range, blacklist)
  tokeniser_reference.tokenise_corpus_from_iterator(sentences_reference)
  ngrams_reference: dict[int, Counter] = tokeniser_reference.get_ngrams()
  keyness_estimator = KeynessEstimator(ngrams_target, ngrams_reference)
  keyness_estimator.estimate_cross_corpus_npmi()
  sorted_key_ngrams: keyness = keyness_estimator.get_top_ngrams(
      npmi_threshold=0,
      min_freq=2,
      symmetric=True # Set this parameter to `True.
  )
  from pprint import pprint
  pprint(sorted_key_ngrams)
  ```

  ```python
  {'negative': {
                1: [('the', 2, 6, -0.027146047077743617)]
               },
   'positive': {
                1: [('relevant', 3, 0, 20.146187299249085),
                    ('target', 3, 1, 2.0723496378521133),
                    ('to', 2, 1, 1.1157023449456727),
                    ('corpus', 3, 4, 0.7390163045187798),
                    ('your', 2, 4, 0.23147412755019178)],
                2: [('target corpus', 3, 1, 1.769345965087366)],
                4: [('relevant to your target', 2, 0, 38.08173668923095)]
               }
  }
  ```

### Streamlined Workflow

If you want a more simplified workflow, use the `StreamedPipeline` which abstracts away most steps.

For extracting Keywords and MWE:

  ```python
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  from key_mwe.workflow import StreamedPipeline
  from nltk.corpus import stopwords

  blacklist = set(stopwords.words("english"))
  mwe_range: list[int] = [2, 3, 4]
  content: str = "Some long content relevant to your target corpus.\nWith multiple sentences relevant to your target corpus.\nThe more target corpus relevant material, the better."
  sentences: list[str] = [sentence for sentence in content.split('\n') if sentence]
  tokeniser = NgramDictTokeniser(mwe_range, blacklist)   
  pipeline = StreamedPipeline()
  npmi_values: dict[int, list[tuple[str, float]]] = pipeline.extract_ngram_features(tokeniser, sentences)
  from pprint import pprint
  pprint(npmi_values)
  ```

For estimating Keyness of Keywords and MWE:

  ```python
  from key_mwe.ngram_dict_tokeniser import NgramDictTokeniser
  from key_mwe.workflow import StreamedPipeline

  blacklist = set(stopwords.words("english"))
  mwe_range: list[int] = [2, 3, 4]
  content: str = "Compared to drugs and even food, cosmetics have been the regulatory stepchild in the Federal Food, Drug, and Cosmetic Act (FFDCA) since its adoption in 1938 - until now. At the end of 2022, Congress enacted legislation to mandate that cosmetic product manufacturers and processors take certain actions that the Food and Drug Administration (FDA) has encouraged them to take for years but for which it had no enforcement authority. Cosmetic producers beware: Increased regulation is coming by the end of 2023. Get ready now.\n\nThe Modernization of Cosmetics Regulation Act of 2022 (MoCRA) was tucked into the omnibus appropriations bill passed at the end of December. MoCRA appears as Subtitle E of Title II of Division H of the 1,653-page Consolidated Appropriations Act, 2023, Public Law 117-328 (Dec. 29, 2022), beginning at section 3501.\n\nThe passage of MoCRA as part of the omnibus illustrates how difficult it has been to enact legislation to strengthen FDA's authority over cosmetics. Since at least 2010, multiple Congresses have considered, but not enacted, cosmetic regulation bills. Legislation similar to MoCRA was introduced in 2017, 2019, and 2021. None passed, partly because of disputes between large and small cosmetic producers, and between the industry and NGOs.\n\nNow, however, Congress has enacted MoCRA, legislation that reflects numerous compromises. Most provisions take effect one year from enactment, or by December 29, 2023. The new labeling requirement becomes effective one year later on December 29, 2024. (MoCRA § 3503(b))\n\nMoCRA is mainly concerned with cosmetic products, a term defined to mean \"a preparation of cosmetic ingredients with a qualitatively and quantitatively set composition for use in a finished product.\" (FFDCA § 604(2)) In other words, a \"cosmetic product\" has been formulated but not necessarily packaged for retail sale. The term does not include chemicals intended for use in a cosmetic product. However, cosmetic ingredient suppliers can expect their customers to ask for help in compliance with some provisions.\n\nSome MoCRA provisions apply to cosmetic product facilities. \"Facility\" refers to an establishment that manufactures or processes cosmetic products distributed in the U.S., including foreign establishments. (FFDCA § 604(3))\n\nIn brief, MoCRA amends the FFDCA to add several new provisions:\n\nIn short, both FDA and cosmetic product manufacturers and processors have a lot of work to do. We understand that FDA is working on MoCRA implementation, but it has not yet commented on MoCRA on its website.\n\nAdverse event reporting (AER) is an early warning system for potential public health issues associated with using FDA-regulated products. It also serves as a mechanism to track patterns of adulteration in FDA-regulated products that supports FDA efforts to target limited inspection resources to protect public health. Until now, FDA's authority to require AER has been limited to prescription and non-prescription drugs, medical devices, biologics, dietary supplements, and food. With MoCRA, add cosmetics to that list.\n\nFDA has a voluntary AER system for cosmetics. MedWatch allows health care professionals and consumers to submit reports to FDA regarding problems with FDA-regulated products, including cosmetics. It also allows cosmetic user facilities, importers, and manufacturers to report using Form FDA 3500A.\n\nFFDCA § 605 only mandates reporting of a serious adverse event. That term is defined to mean an adverse event (i.e., any adverse health-related event associated with use of a cosmetic) that results in death, life-threatening experience, in-patient hospitalization, persistent or significant disability or incapacity, congenital anomaly or birth defect, an infection, serious disfigurement, or requires a medical or surgical intervention to prevent such an outcome. (FFDCA § 604(1), (5)) The reporting obligation would apply to any \"responsible party,\" including the manufacturer, packer, or distributor whose name appears on the cosmetic product's label. (FFDCA §§ 604(4), 605(a))\n\nCosmetic product manufacturers and distributors may want to familiarize themselves with the MedWatch system, as the new system may be similar.\n\nFDA has good manufacturing practice (GMP) regulations for other products it regulates. Without statutory authority to require GMPs for cosmetics, FDA has instead provided voluntary cosmetic product GMP guidance (2013, although still a draft).\n\nFFDCA § 606 directs FDA to adopt mandatory GMP regulations for cosmetic products, with simplified requirements for smaller businesses. The regulations are to be generally consistent with national and international standards. Since the FDA voluntary GMP guidance is brief, cosmetic product manufacturers, processors, and distributors may want to review ISO 22715:2006, Cosmetics - Packaging and labelling (last reviewed and confirmed in 2022). This international standard has provisions on personnel, premises, raw materials, packaging materials, production, finished products, quality control laboratory, dealing with out-of-specification results, complaints, recalls, change control, internal audits, and documentation.\n\nFDA must publish its proposed regulations by December 29, 2024, and its final regulations by December 29, 2025.\n\nFFDCA § 607(a) requires the owners and operators of existing cosmetic product facilities in the U.S. or that distribute to the U.S. to register with FDA by December 29, 2023. New facilities must be registered within 60 days of startup. Registrations will need to be renewed every two years, with changes to registration information to be reported within 60 days of the change. Registration will have significance since FDA can suspend a registration if it determines that the cosmetic products manufactured or processed at the facility may cause serious health consequences or death. A suspension would preclude the distribution of cosmetic products from that facility. (FFDCA § 607(f))\n\nSince 1974, FDA has promoted a Voluntary Cosmetic Registration Program. (21 C.F.R. Part 710) As the mandatory registration program is likely to be similar to the voluntary one, owners and operators of cosmetic product facilities in the U.S. or that distribute into the U.S. may want to review Part 710 and consider submitting Form FDA 2511 to register their facilities, if they have not already done so.\n\nFFDCA § 607(c) requires the responsible person for each cosmetic product currently marketed in the U.S. to list that product with FDA by December 29, 2023. New cosmetic products must be listed within 120 days of being marketed. Updated information must be submitted annually. Among other information, a product listing must include a list of ingredients, including fragrances, flavors, or colors, as provided in 21 C.F.R. § 701.3.\n\nFDA's Voluntary Cosmetic Registration Program includes voluntary product listing, referred to as voluntary filing of cosmetic product ingredient composition statements. (21 C.F.R. Part 720) As the mandatory product listing program is likely to be similar to the voluntary one, responsible persons may want to review Part 720 and consider submitting Form FDA 2512 for their cosmetic products if they have not already done so.\n\nFDA regulations currently require safety substantiation:\n\nEach ingredient used in a cosmetic product and each finished cosmetic product shall be adequately substantiated for safety prior to marketing. Any such ingredient or product whose safety is not adequately substantiated prior to marketing is misbranded unless it contains the following conspicuous statement on the principal display panel: \"Warning - The safety of this product has not been determined.\"\n\n21 C.F.R. § 740.10(a). FFDCA § 608 will bolster that requirement.\n\nIt requires the responsible person for a cosmetic product to ensure adequate substantiation of the product's safety, and to maintain records supporting that substantiation. \"Adequate substantiation of safety\" refers to tests, studies, research, or other information that is considered, among qualified experts, to be sufficient to support a reasonable certainty that a cosmetic product is safe. (FFDCA § 606(c)(1)) \"Safe\" means that the cosmetic product, including its ingredients, is not injurious to users under label conditions or customary or usual conditions. (FFDCA § 606(c)(2)) Cosmetic ingredient suppliers may expect requests from cosmetic product manufacturers for substantiation of the safety of their ingredients.\n\nThe FFDCA § 608 safety substantiation requirement takes effect on December 29, 2023. (MoCRA § 3503(b)(1)) Before that date, responsible persons should confirm that they have documentation to support that their cosmetic products have adequate substantiations of safety.\n\nFDA already has some labeling requirements for cosmetic products, 21 C.F.R. Part 701, and cosmetics labeling guidance. FFDCA § 609 supplements those requirements and that guidance. Labels meeting the new requirements are required for cosmetic products marketed on or after December 29, 2024. (MoCRA § 3503(b)(2))\n\nThe new label must:\n\nThe Factory Inspection authority of FFDCA § 704 extends to cosmetic product facilities. MoCRA § 3504 amended FFDCA § 704 to specify that inspections \"shall\" cover records and other information related to serious adverse event reporting, GMPs, and records covered by FFDCA § 610.\n\nFFDCA § 610 authorizes FDA to have access to all records related to cosmetic products and their ingredients which it reasonably believes may be adulterated to present a threat of serious adverse consequences or death.\n\nThis records access provision does not extend to recipes or formulas for cosmetics, financial data, pricing data, or personnel data (other than with respect to their qualifications), research data (other than safety substantiation data), or sales data (other than shipment data).\n\nWith FFDCA § 611, FDA now has recall authority for cosmetic products which it reasonably determines may be adulterated (including due to noncompliance with the new GMP or safety substantiation requirements) or misbranded (including due to noncompliance with the new labeling requirements). (MoCRA § 3503(a)(2), (3))\n\nThe provision lays out several procedural protections, including the requirement that FDA provide an opportunity for a voluntary recall.\n\nUnder FFDCA § 612, with some exceptions, small businesses (those with gross annual sales less than $1 million (adjusted for inflation)) are not subject to the GMP or facility registration and product listing requirements.\n\nUnder FFDCA § 613, cosmetic products that are also drugs are exempt from most MoCRA requirements. Facilities that manufacture or process cosmetic products subject to drug requirements are also exempt.\n\nMoCRA adds a new express preemption provision, FFDCA § 614(a). In general, no state or locality may impose any requirement for cosmetics regarding registration and product listing, GMPs, records, recalls, adverse event reporting, or safety substantiation that is not identical to the federal requirement.\n\nImportant exclusions from this preemption provision in FFDCA § 614(b) include state requirements:\n\nThis preemption provision does not affect the provision on preemption of requirements for labeling or packaging cosmetics in FFDCA § 752.\n\nSome cosmetics contain talc, and talc may potentially contain asbestos. FDA reports annual results from testing cosmetic products containing talc to see if they also contain asbestos.\n\nMoCRA § 3505 directs FDA to adopt regulations on standardized testing methods for detecting and identifying asbestos in talc-containing cosmetic products. The proposed rule is due by December 29, 2023. The final rule is due 180 days later.\n\nThe FDA website confirms that, \"PFAS are used as ingredients in certain cosmetics, such as lotions, cleansers, nail polish, shaving cream, and some types of makeup, such as lipstick, eyeliner, eyeshadow, and mascara.\"\n\nMoCRA § 3507 directs FDA to issue a report assessing the safety of using PFAS in cosmetic products. The report is due by December 29, 2025.\n\nAn FDA policy statement on animal testing says that \"animal testing by manufacturers seeking to market new products may be used to establish product safety\" after consideration of alternatives.\n\nMoCRA § 3507 conveys the sense of the Congress that:\n\nanimal testing should not be used for the purposes of safety testing on cosmetic products and should be phased out with the exception of appropriate allowances.\n\nThis provision does not bind FDA or manufacturers or processors of cosmetic products."
  sentences_positive: list[str] = [sentence for sentence in content.split('\n') if sentence]
  content_reference: list[str] = [
    "Content that is unrelated to your target corpus.\nUse as many orthogonal domains as possible.",
    "Long content for domain A, as part of your reference corpus.\nWith multiple sentences.\nThe more the better.",
    "Long content for domain B, as part of your reference corpus.\nWith multiple sentences.\nThe more the better.",
    "Long content for domain C, as part of your reference corpus.\nWith multiple sentences.\nThe more the better."  
  ]
  sentences_reference: list[str] = [sentence for content in content_reference for sentence in content.split("\n")]
  tokeniser_positive = NgramDictTokeniser(mwe_range, blacklist)
  tokeniser_negative = NgramDictTokeniser(mwe_range, blacklist)
  pipeline = StreamedPipeline()
  keyness_values = pipeline.extract_key_ngram_features(
      tokeniser_positive, 
      tokeniser_negative, 
      sentences_positive, 
      sentences_reference
  )
  print(keyness_values)
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
