import pytest
from unittest.mock import patch, MagicMock
import os
from modules import ContentGenerator

def test_content_generator_initialization():
    generator = ContentGenerator()
    assert generator is not None
    assert generator.openai_api_key is not None
    assert generator.amazon_tag is not None

def test_init_missing_env_vars():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            ContentGenerator()

@patch('openai.OpenAI')
def test_create_post(mock_openai):
    # Mock OpenAI client response
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content="Test caption"))
    ]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client

    generator = ContentGenerator()
    trend = {
        'query': 'natural skincare routine',
        'category': 'skincare',
        'volume': 1000
    }

    content = generator.create_post(trend)
    assert content is not None
    assert 'caption' in content
    assert 'image_url' in content
    assert 'affiliate_link' in content
    assert 'skincare' in content['caption'].lower()  # Check for relevant content
