import pytest
from modules.trends import TrendAnalyzer
from unittest.mock import patch

@pytest.fixture
def mock_analyzer():
    analyzer = TrendAnalyzer()
    analyzer.pinterest_token = "pinterest_test123"
    return analyzer

def test_token_validation(mock_analyzer):
    assert mock_analyzer._check_token_valid()
    mock_analyzer.pinterest_token = "invalid"
    assert not mock_analyzer._check_token_valid()

@patch('requests.get')
def test_api_error_handling(mock_get, mock_analyzer):
    mock_get.return_value.status_code = 500
    assert mock_analyzer.get_pinterest_trends() == [] 