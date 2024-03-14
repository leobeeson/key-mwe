import pytest


from src.key_mwe.text_preprocessor import Preprocessor


@pytest.fixture
def preprocessor() -> Preprocessor:
    """Fixture to create a Preprocessor object for testing."""
    return Preprocessor()


class TestPreprocessor:

    def test_custom_strip_punctuation(self, preprocessor: Preprocessor) -> None:
        """Test the removal of punctuation from a sentence."""
        sentence = "Hello, world! ¿Cómo están?"
        expected = "Hello ZULUZULU  world ZULUZULU   ZULUZULU Cómo están ZULUZULU "
        assert preprocessor.custom_strip_punctuation(sentence) == expected


    def test_custom_strip_non_alphanumeric(self, preprocessor: Preprocessor) -> None:
        """Test the removal of non-alphanumeric characters, preserving spaces and accented letters."""
        sentence = "Python 3.8+ ¿Es mejor? ¡Claro que sí!"
        expected = "Python 3 8 Es mejor Claro que sí "
        assert preprocessor.custom_strip_non_alphanumeric(sentence) == expected


    def test_clean_line_basic(self, preprocessor: Preprocessor) -> None:
        """Test basic cleaning without lowercasing."""
        sentence = "<p>Hello, <b>world</b>! ¿Cómo están?</p>"
        expected = "Hello ZULUZULU world ZULUZULU ZULUZULU Cómo están ZULUZULU"
        assert preprocessor.clean_line(sentence, lower_case=False) == expected


    def test_clean_line_lowercase(self, preprocessor: Preprocessor) -> None:
        """Test cleaning with lowercasing."""
        sentence = "<p>Hello, <b>WORLD</b>! ¿Cómo ESTÁN?</p>"
        expected = "hello zuluzulu world zuluzulu zuluzulu cómo están zuluzulu"
        assert preprocessor.clean_line(sentence, lower_case=True) == expected


    def test_clean_line_integration(self, preprocessor: Preprocessor) -> None:
        """Test the integrated cleaning process with all custom filters and lowercasing."""
        sentence = "<p>Hello, WORLD! ¿Cómo ESTÁN? Numbers: 1234.</p>"
        expected = "hello zuluzulu world zuluzulu zuluzulu cómo están zuluzulu numbers zuluzulu 1234 zuluzulu"
        assert preprocessor.clean_line(sentence) == expected
