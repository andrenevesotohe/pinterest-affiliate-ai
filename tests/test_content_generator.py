"""Tests for the ContentGenerator class."""

import pytest
from unittest.mock import Mock, patch
from modules.content_generator import ContentGenerator
from modules.dalle_generator import DalleBeautyGenerator

@pytest.fixture
def mock_openai_response():
    return Mock(data=[Mock(url="https://test-image-url.com")])

@pytest.fixture
def content_generator():
    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'AMAZON_ASSOCIATE_TAG': 'test-tag'
    }):
        return ContentGenerator()

def test_content_generator_initialization(content_generator):
    """Test ContentGenerator initialization."""
    assert content_generator.openai_api_key == 'test-key'
    assert content_generator.amazon_tag == 'test-tag'
    assert isinstance(content_generator.dalle_generator, DalleBeautyGenerator)

@patch('openai.OpenAI')
def test_generate_dalle_image_success(mock_openai, content_generator, mock_openai_response):
    """Test successful DALL-E image generation."""
    mock_client = Mock()
    mock_client.images.generate.return_value = mock_openai_response
    mock_openai.return_value = mock_client

    product = {'name': 'retinol serum', 'category': 'skincare'}
    trend = {'query': 'retinol serum', 'category': 'skincare'}
    
    image_url = content_generator._generate_dalle_image(product, trend)
    
    assert image_url == "https://test-image-url.com"
    mock_client.images.generate.assert_called_once()

def test_create_post_success(content_generator):
    """Test successful post creation."""
    with patch.object(content_generator, '_generate_dalle_image') as mock_image, \
         patch.object(content_generator.text_generator, 'generate_text') as mock_text:
        
        mock_image.return_value = "https://test-image.com"
        mock_text.return_value = "Test caption"
        
        trend = {
            'query': 'vitamin c serum',
            'category': 'skincare'
        }
        
        post = content_generator.create_post(trend)
        
        assert post is not None
        assert post['image_url'] == "https://test-image.com"
        assert post['caption'] == "Test caption"
        assert 'vitamin+c+serum' in post['affiliate_link']
        assert 'test-tag' in post['affiliate_link']

def test_create_post_image_failure(content_generator):
    """Test post creation when image generation fails."""
    with patch.object(content_generator, '_generate_dalle_image') as mock_image:
        mock_image.return_value = None
        
        trend = {
            'query': 'vitamin c serum',
            'category': 'skincare'
        }
        
        post = content_generator.create_post(trend)
        assert post is None

def test_get_key_benefit(content_generator):
    """Test key benefit extraction."""
    trend_skincare = {'category': 'skincare'}
    assert 'radiant' in content_generator._get_key_benefit(trend_skincare)
    
    trend_haircare = {'category': 'haircare'}
    assert 'stronger' in content_generator._get_key_benefit(trend_haircare)
    
    trend_makeup = {'category': 'makeup'}
    assert 'flawless' in content_generator._get_key_benefit(trend_makeup)

def test_get_affiliate_link(content_generator):
    """Test affiliate link generation."""
    trend = {
        'query': 'face moisturizer',
        'category': 'skincare'
    }
    
    link = content_generator._get_affiliate_link(trend)
    assert 'face+moisturizer' in link
    assert 'skincare+beauty' in link
    assert content_generator.amazon_tag in link
