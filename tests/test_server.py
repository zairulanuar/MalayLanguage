"""
Tests for MalayLanguage MCP Server
"""
import pytest
import sys
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Mock malaya module before importing server
sys.modules['malaya'] = MagicMock()
sys.modules['malaya.language_detection'] = MagicMock()
sys.modules['malaya.normalize'] = MagicMock()
sys.modules['malaya.spelling_correction'] = MagicMock()
sys.modules['malaya.translation'] = MagicMock()
sys.modules['malaya.paraphrase'] = MagicMock()

from server import (
    detect_language,
    normalize_malay,
    correct_spelling,
    apply_glossary,
    rewrite_style,
    translate,
    term_lookup,
)


class MockModel:
    """Mock model for testing."""
    
    def predict(self, texts):
        """Mock predict method."""
        return [{"label": "malay", "score": 0.95} for _ in texts]
    
    def normalize(self, text):
        """Mock normalize method."""
        return text.lower()
    
    def correct(self, text):
        """Mock correct method."""
        return text.replace("saya", "Saya")
    
    def translate(self, texts):
        """Mock translate method."""
        return [f"translated: {text}" for text in texts]
    
    def paraphrase(self, texts):
        """Mock paraphrase method."""
        return [f"paraphrased: {text}" for text in texts]


@pytest.fixture
def mock_models():
    """Fixture to mock all model loading functions."""
    with patch("server.get_language_detection_model") as lang_mock, \
         patch("server.get_normalizer_model") as norm_mock, \
         patch("server.get_spelling_corrector") as spell_mock, \
         patch("server.get_translation_model") as trans_mock, \
         patch("server.get_paraphrase_model") as para_mock:
        
        mock_model = MockModel()
        lang_mock.return_value = mock_model
        norm_mock.return_value = mock_model
        spell_mock.return_value = mock_model
        trans_mock.return_value = mock_model
        para_mock.return_value = mock_model
        
        yield {
            "language": lang_mock,
            "normalizer": norm_mock,
            "spelling": spell_mock,
            "translation": trans_mock,
            "paraphrase": para_mock,
        }


@pytest.mark.asyncio
async def test_detect_language(mock_models):
    """Test language detection tool."""
    result = await detect_language("Ini adalah teks Melayu")
    assert len(result) == 1
    assert "Language: malay" in result[0].text
    assert "Confidence:" in result[0].text


@pytest.mark.asyncio
async def test_detect_language_empty():
    """Test language detection with empty text."""
    result = await detect_language("")
    assert len(result) == 1
    assert "Error: Empty or whitespace-only text" in result[0].text


@pytest.mark.asyncio
async def test_normalize_malay(mock_models):
    """Test Malay text normalization."""
    result = await normalize_malay("Saya SUKA Makanan")
    assert len(result) == 1
    assert "Original:" in result[0].text
    assert "Normalized:" in result[0].text


@pytest.mark.asyncio
async def test_normalize_malay_empty():
    """Test normalization with empty text."""
    result = await normalize_malay("")
    assert len(result) == 1
    assert "Error: Empty or whitespace-only text" in result[0].text


@pytest.mark.asyncio
async def test_correct_spelling(mock_models):
    """Test spelling correction."""
    result = await correct_spelling("saya suka makan")
    assert len(result) == 1
    assert "Original:" in result[0].text
    assert "Corrected:" in result[0].text


@pytest.mark.asyncio
async def test_correct_spelling_empty():
    """Test spelling correction with empty text."""
    result = await correct_spelling("")
    assert len(result) == 1
    assert "Error: Empty or whitespace-only text" in result[0].text


@pytest.mark.asyncio
async def test_apply_glossary(mock_models):
    """Test glossary lookup."""
    result = await apply_glossary("makan")
    assert len(result) == 1
    assert "Glossary Lookup: makan" in result[0].text
    assert "Translation" in result[0].text


@pytest.mark.asyncio
async def test_apply_glossary_empty():
    """Test glossary lookup with empty term."""
    result = await apply_glossary("")
    assert len(result) == 1
    assert "Error: Empty or whitespace-only term" in result[0].text


@pytest.mark.asyncio
async def test_rewrite_style(mock_models):
    """Test style rewriting."""
    result = await rewrite_style("Saya suka makan nasi", "formal")
    assert len(result) == 1
    assert "Original:" in result[0].text
    assert "Rewritten:" in result[0].text


@pytest.mark.asyncio
async def test_rewrite_style_empty():
    """Test style rewriting with empty text."""
    result = await rewrite_style("", "formal")
    assert len(result) == 1
    assert "Error: Empty or whitespace-only text" in result[0].text


@pytest.mark.asyncio
async def test_translate(mock_models):
    """Test translation."""
    result = await translate("Selamat pagi", "ms", "en")
    assert len(result) == 1
    assert "Source (Malay):" in result[0].text
    assert "Translation (English):" in result[0].text


@pytest.mark.asyncio
async def test_translate_empty():
    """Test translation with empty text."""
    result = await translate("", "ms", "en")
    assert len(result) == 1
    assert "Error: Empty or whitespace-only text" in result[0].text


@pytest.mark.asyncio
async def test_translate_same_language(mock_models):
    """Test translation with same source and target language."""
    result = await translate("Hello", "en", "en")
    assert len(result) == 1
    assert "Error: Source and target languages must be different" in result[0].text


@pytest.mark.asyncio
async def test_term_lookup(mock_models):
    """Test term lookup."""
    result = await term_lookup("makan")
    assert len(result) == 1
    assert "Term Lookup: makan" in result[0].text
    assert "Language:" in result[0].text
    assert "Translation:" in result[0].text


@pytest.mark.asyncio
async def test_term_lookup_empty():
    """Test term lookup with empty term."""
    result = await term_lookup("")
    assert len(result) == 1
    assert "Error: Empty or whitespace-only term" in result[0].text
