import pytest
from unittest.mock import patch, MagicMock
from modules.poster import PinterestPoster
import os
import requests

# Test Fixtures
@pytest.fixture
def mock_poster():
    """Fixture providing a PinterestPoster with mocked env vars"""
    with patch.dict(os.environ, {
        "PINTEREST_API_KEY": "test_token_123",
        "PINTEREST_BOARD_ID": "test_board_456"
    }):
        yield PinterestPoster()

@pytest.fixture
def sample_post_data():
    return {
        "image_url": "https://example.com/image.jpg",
        "caption": "Test caption #beauty",
        "link": "https://example.com/affiliate?tag=test123"
    }

# Tests
class TestPinterestPoster:
    def test_initialization(self, mock_poster):
        """Verify environment variables are loaded correctly"""
        assert mock_poster.token == "test_token_123"
        assert mock_poster.board_id == "test_board_456"

    @patch('requests.post')
    def test_successful_post(self, mock_post, mock_poster, sample_post_data):
        """Test successful API response"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "pin_123"}
        mock_post.return_value = mock_response

        # Execute
        result = mock_poster.post(
            image_url=sample_post_data["image_url"],
            caption=sample_post_data["caption"],
            link=sample_post_data["link"]
        )

        # Verify
        assert result is True
        mock_post.assert_called_once_with(
            "https://api.pinterest.com/v5/pins",
            headers={"Authorization": "Bearer test_token_123"},
            json={
                "title": "Beauty Find 🧴",
                "description": "Test caption #beauty\n\n#AffiliateLink",
                "board_id": "test_board_456",
                "media": {"source_type": "image_url", "url": "https://example.com/image.jpg"},
                "link": "https://example.com/affiliate?tag=test123"
            },
            timeout=10
        )

    @patch('requests.post')
    def test_failed_post(self, mock_post, mock_poster, sample_post_data):
        """Test failed API response"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        result = mock_poster.post(
            image_url=sample_post_data["image_url"],
            caption=sample_post_data["caption"],
            link=sample_post_data["link"]
        )

        assert result is False

    @patch('requests.post')
    def test_rate_limiting(self, mock_post, mock_poster, sample_post_data):
        """Verify rate limiting decorator is applied"""
        import inspect
        from ratelimit import limits

        # Check decorator exists
        post_method = mock_poster.post.__wrapped__  # Access original undecorated function
        decorators = inspect.getattr_static(post_method, "__wrapped__", None)
        assert hasattr(post_method, "_ratelimit"), "Rate limiting not applied"
        assert post_method._ratelimit == {'calls': 5, 'period': 60}

    @patch('requests.post')
    def test_timeout_handling(self, mock_post, mock_poster, sample_post_data):
        """Test request timeout handling"""
        mock_post.side_effect = requests.exceptions.Timeout()

        result = mock_poster.post(
            image_url=sample_post_data["image_url"],
            caption=sample_post_data["caption"],
            link=sample_post_data["link"]
        )

        assert result is False

    @patch('requests.post')
    def test_retry_mechanism(self, mock_post, mock_poster, sample_post_data):
        """Verify retry on temporary failures"""
        # First attempt fails, second succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 429
        mock_response_success = MagicMock()
        mock_response_success.status_code = 201
        mock_post.side_effect = [mock_response_fail, mock_response_success]

        result = mock_poster.post(
            image_url=sample_post_data["image_url"],
            caption=sample_post_data["caption"],
            link=sample_post_data["link"]
        )

        assert result is True
        assert mock_post.call_count == 2

# Integration Test
class TestIntegration:
    @patch('modules.poster.requests.post')
    def test_full_post_cycle(self, mock_post, mock_poster, sample_post_data):
        """End-to-end test with mocked dependencies"""
        from modules.trends import TrendAnalyzer
        from modules.poster import PinterestPoster

        # Setup mocks
        mock_post.return_value.status_code = 201
        with patch.object(TrendAnalyzer, 'get_daily_beauty_trends') as mock_trends:
            mock_trends.return_value = [{
                'query': 'test trend',
                'category': 'skincare',
                'volume': 1000
            }]

            # Execute
            poster = PinterestPoster()
            result = poster.post(**sample_post_data)

            # Verify
            assert result is True
            mock_post.assert_called_once()
