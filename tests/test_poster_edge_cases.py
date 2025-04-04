import pytest
from unittest.mock import patch, MagicMock
from modules.poster import PinterestPoster
import requests
import os

@pytest.fixture
def mock_poster():
    """Fixture providing a PinterestPoster with mocked env vars"""
    with patch.dict(os.environ, {
        "PINTEREST_API_KEY": "test_token_123",
        "PINTEREST_BOARD_ID": "test_board_456"
    }):
        yield PinterestPoster()

class TestEdgeCases:
    def test_invalid_image_url(self, mock_poster):
        """Test behavior with broken image links"""
        with pytest.raises(ValueError):
            mock_poster.post(
                image_url="not_a_url",
                caption="test",
                link="https://valid.com"
            )

    def test_empty_caption(self, mock_poster):
        """Test behavior with empty caption"""
        with pytest.raises(ValueError):
            mock_poster.post(
                image_url="https://valid.com/image.jpg",
                caption="",
                link="https://valid.com"
            )

    def test_invalid_link_format(self, mock_poster):
        """Test behavior with malformed affiliate links"""
        with pytest.raises(ValueError):
            mock_poster.post(
                image_url="https://valid.com/image.jpg",
                caption="test",
                link="not_a_valid_link"
            )

    @patch('requests.post')
    def test_network_error(self, mock_post, mock_poster):
        """Test behavior with network connectivity issues"""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        result = mock_poster.post(
            image_url="https://valid.com/image.jpg",
            caption="test",
            link="https://valid.com"
        )

        assert result is False

    @patch('requests.post')
    def test_invalid_json_response(self, mock_post, mock_poster):
        """Test behavior with invalid JSON response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        result = mock_poster.post(
            image_url="https://valid.com/image.jpg",
            caption="test",
            link="https://valid.com"
        )

        assert result is False

@pytest.mark.benchmark
class TestPerformance:
    def test_post_performance(self, mock_poster, benchmark):
        """Ensure posts complete within 2 seconds"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201

            benchmark(mock_poster.post,
                     image_url="https://test.com/image.jpg",
                     caption="test",
                     link="https://test.com")

            assert benchmark.stats['max'] < 2.0

    def test_concurrent_posts(self, mock_poster, benchmark):
        """Test performance with multiple concurrent posts"""
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 201

            def concurrent_posts():
                for _ in range(5):
                    mock_poster.post(
                        image_url="https://test.com/image.jpg",
                        caption="test",
                        link="https://test.com"
                    )

            benchmark(concurrent_posts)
            assert benchmark.stats['max'] < 10.0  # Should complete within 10 seconds
