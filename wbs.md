# Work Breakdown Structure

## High-Level Structure

1. Data Ingestor
2. Text Preprocessor
3. Ngram Tokeniser
4. Within-Corpus NPMI Estimator
5. Cross-Corpus NPMI Estimator
6. Workflows

## Data Ingestor

- Implement ingestor from `Iterator[str]` in Ngram Tokeniser. #DONE

## Text Preprocessor

- Import wikipedia `es` data preprocessor. #DONE
- Implement baseline unit tests. #DONE

## Ngram Tokeniser

- Import wikipedia `es` data ngram dict tokeniser. #DONE
- Implement baseline unit tests. #DONE
- Configure separator token as configurable var. #DONE
- Inhibit ngrams with separator token. #DONE

## Within-Corpus NPMI Estimator

- Import wikipedia `es` data NPMI Estimator. #DONE
- Implement unit tests for probs and npmi calculations. #DONE

## Cross-Corpora NPMI Estimator

- Import wikipedia `es` data Cross-Corpora NPMI Estimator. #DONE
- Implement baseline unit tests. #DONE
- Implement unit tests for probs and npmi calculations. #DONE

## Workflows

- Define key definitions. #DONE
- Identify types of use case workflows. #DONE
- Document use case workflows. #DONE
- Implement streamed corpus ngram extraction. #DONE
- Implement streamed corpus keyness estimation. #DONE
- Implement ingest from disc ngram extraction. #SOMEDAY
- Implement ingest from disc keyness estimation. #SOMEDAY
