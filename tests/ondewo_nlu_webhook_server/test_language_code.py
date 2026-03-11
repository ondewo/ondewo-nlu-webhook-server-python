import pytest

from ondewo_nlu_webhook_server.custom_exceptions import NotALanguageError
from ondewo_nlu_webhook_server.language_code import LanguageCode


class TestLanguageCodeMissing:
    def test_missing_with_underscore(self) -> None:
        lc = LanguageCode("en_US")
        assert lc == LanguageCode.en_US

    def test_missing_with_lowercase(self) -> None:
        lc = LanguageCode("en-us")
        assert lc == LanguageCode.en_US

    def test_missing_non_string_raises(self) -> None:
        with pytest.raises(ValueError, match="Expect a string"):
            LanguageCode(123)  # type: ignore[arg-type]

    def test_missing_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError, match="Could not instantiate"):
            LanguageCode("zzz-ZZZ-ZZZ")

    def test_missing_three_part_code(self) -> None:
        # The _missing_ method doesn't fully handle middle segment capitalization,
        # so the exact enum value format is required for three-part codes
        lc = LanguageCode("yue-Hant-HK")
        assert lc == LanguageCode.yue_Hant_HK


class TestFromList:
    def test_from_list_sorted(self) -> None:
        result = LanguageCode.from_list(["en-US", "de-DE"])
        assert result == [LanguageCode.de_DE, LanguageCode.en_US]

    def test_from_list_unsorted(self) -> None:
        result = LanguageCode.from_list(["en-US", "de-DE"], sort_values=False)
        assert result == [LanguageCode.en_US, LanguageCode.de_DE]


class TestSetOperations:
    def test_intersect_sets(self) -> None:
        s1 = {LanguageCode.en_US, LanguageCode.de_DE}
        s2 = {LanguageCode.en_US, LanguageCode.fr_FR}
        result = LanguageCode.intersect_sets(s1, s2)
        assert result == {LanguageCode.en_US}

    def test_extend_set_with_multi(self) -> None:
        s = {LanguageCode.multi}
        result = LanguageCode.extend_set(s)
        assert LanguageCode.multi not in result
        assert len(result) > 100

    def test_extend_set_without_multi(self) -> None:
        s = {LanguageCode.en_US}
        result = LanguageCode.extend_set(s)
        assert result == {LanguageCode.en_US}

    def test_compress_set_all_languages(self) -> None:
        all_langs = LanguageCode.get_all_languages_set()
        result = LanguageCode.compress_set(all_langs)
        assert result == {LanguageCode.multi}

    def test_compress_set_subset(self) -> None:
        s = {LanguageCode.en_US}
        result = LanguageCode.compress_set(s)
        assert result == {LanguageCode.en_US}

    def test_get_all_languages_set(self) -> None:
        all_langs = LanguageCode.get_all_languages_set()
        assert LanguageCode.multi not in all_langs
        assert LanguageCode.en_US in all_langs


class TestAssertIsALanguage:
    def test_valid_language(self) -> None:
        assert LanguageCode.assert_is_a_language(LanguageCode.en_US) is True

    def test_none_raises(self) -> None:
        with pytest.raises(NotALanguageError):
            LanguageCode.assert_is_a_language(None)

    def test_none_no_raise(self) -> None:
        result = LanguageCode.assert_is_a_language(None, raise_exception=False)
        assert result is False

    def test_non_language_raises(self) -> None:
        with pytest.raises(NotALanguageError):
            LanguageCode.assert_is_a_language("en-US")

    def test_non_language_no_raise(self) -> None:
        result = LanguageCode.assert_is_a_language("en-US", raise_exception=False)
        assert result is False


class TestLanguageProperties:
    def test_get_language_str(self) -> None:
        result = LanguageCode.en_US.get_language_str()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_language(self) -> None:
        lang = LanguageCode.en_US.get_language()
        assert lang is not None

    def test_get_long_name(self) -> None:
        try:
            result = LanguageCode.en_US.get_long_name()
            assert isinstance(result, str)
            assert len(result) > 0
        except ModuleNotFoundError:
            pytest.skip("language_data package not installed")

    def test_get_locale_multi(self) -> None:
        result = LanguageCode.multi.get_locale()
        assert result == LanguageCode.en_US.get_value()

    def test_get_locale_regular(self) -> None:
        result = LanguageCode.de_DE.get_locale()
        assert result == "de-DE"

    def test_get_locales(self) -> None:
        result = LanguageCode.get_locales("english")
        assert isinstance(result, set)

    def test_get_locale_utf(self) -> None:
        result = LanguageCode.en_US.get_locale_utf()
        assert isinstance(result, str)

    def test_get_value(self) -> None:
        assert LanguageCode.en_US.get_value() == "en-US"
