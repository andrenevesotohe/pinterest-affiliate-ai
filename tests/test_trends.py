import pytest
from unittest.mock import patch
from modules import TrendAnalyzer

def test_trend_analyzer_initialization():
    analyzer = TrendAnalyzer()
    assert analyzer is not None
    assert analyzer.pinterest_token is not None

def test_token_validation():
    analyzer = TrendAnalyzer()
    assert analyzer._check_token_valid()

@patch('requests.get')
def test_api_error_handling(mock_get):
    analyzer = TrendAnalyzer()
    mock_get.side_effect = Exception("API Error")
    assert analyzer.get_pinterest_trends() == []

def test_get_daily_beauty_trends():
    analyzer = TrendAnalyzer()
    trends = analyzer.get_daily_beauty_trends(max_trends=2)
    assert isinstance(trends, list)
    # Since we're using a real API token, we don't assert the length
    # as it depends on actual API response
