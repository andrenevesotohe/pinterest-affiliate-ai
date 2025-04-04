import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock
from modules.poster import PinterestPoster
from scripts.process_fallback import process_fallback_queue

@pytest.fixture
def mock_fallback_queue():
    """Fixture providing a mock fallback queue."""
    return [
        {
            "image_url": "https://example.com/image1.jpg",
            "caption": "Test caption 1 #beauty",
            "link": "https://example.com/affiliate?tag=test123",
            "attempted_at": "2023-01-01T12:00:00"
        },
        {
            "image_url": "https://example.com/image2.jpg",
            "caption": "Test caption 2 #beauty",
            "link": "https://example.com/affiliate?tag=test123",
            "attempted_at": "2023-01-01T12:30:00"
        }
    ]

def test_process_fallback_queue_empty():
    """Test processing an empty fallback queue."""
    with patch('os.path.exists', return_value=False):
        result = process_fallback_queue()
        assert result == 0

def test_process_fallback_queue_with_mock(mock_fallback_queue):
    """Test processing a fallback queue with mocked poster."""
    # Mock file operations
    mock_file = mock_open(read_data=json.dumps(mock_fallback_queue))
    
    # Mock PinterestPoster
    mock_poster = MagicMock()
    mock_poster.post.side_effect = [True, False]  # First post succeeds, second fails
    
    with patch('builtins.open', mock_file), \
         patch('os.path.exists', return_value=True), \
         patch('modules.poster.PinterestPoster', return_value=mock_poster):
        
        result = process_fallback_queue()
        
        # Check that post was called twice
        assert mock_poster.post.call_count == 2
        
        # Check that only one post was successful
        assert result == 1
        
        # Check that the queue was updated with the failed post
        args, _ = mock_file().write.call_args
        updated_queue = json.loads(args[0])
        assert len(updated_queue) == 1
        assert updated_queue[0]["caption"] == "Test caption 2 #beauty"

def test_process_fallback_queue_with_limit(mock_fallback_queue):
    """Test processing a fallback queue with a limit."""
    # Mock file operations
    mock_file = mock_open(read_data=json.dumps(mock_fallback_queue))
    
    # Mock PinterestPoster
    mock_poster = MagicMock()
    mock_poster.post.return_value = True
    
    with patch('builtins.open', mock_file), \
         patch('os.path.exists', return_value=True), \
         patch('modules.poster.PinterestPoster', return_value=mock_poster):
        
        result = process_fallback_queue(limit=1)
        
        # Check that post was called only once
        assert mock_poster.post.call_count == 1
        
        # Check that only one post was processed
        assert result == 1
        
        # Check that the queue was updated with the remaining post
        args, _ = mock_file().write.call_args
        updated_queue = json.loads(args[0])
        assert len(updated_queue) == 1
        assert updated_queue[0]["caption"] == "Test caption 2 #beauty"

def test_process_fallback_queue_with_exception(mock_fallback_queue):
    """Test processing a fallback queue with an exception."""
    # Mock file operations
    mock_file = mock_open(read_data=json.dumps(mock_fallback_queue))
    
    # Mock PinterestPoster to raise an exception
    mock_poster = MagicMock()
    mock_poster.post.side_effect = Exception("API Error")
    
    with patch('builtins.open', mock_file), \
         patch('os.path.exists', return_value=True), \
         patch('modules.poster.PinterestPoster', return_value=mock_poster):
        
        result = process_fallback_queue()
        
        # Check that post was called twice
        assert mock_poster.post.call_count == 2
        
        # Check that no posts were successful
        assert result == 0
        
        # Check that the queue was updated with both posts (they failed)
        args, _ = mock_file().write.call_args
        updated_queue = json.loads(args[0])
        assert len(updated_queue) == 2 