import pytest
from unittest.mock import patch, mock_open
import json
from datetime import datetime, timedelta
from modules.budget_tracker import DalleBudgetTracker, BudgetExceededError

@pytest.fixture
def budget_tracker():
    """Fixture providing a DalleBudgetTracker with mocked state."""
    with patch('modules.budget_tracker.datetime') as mock_datetime:
        # Set current time to noon
        mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        yield DalleBudgetTracker(daily_limit=0.20)

def test_initialization(budget_tracker):
    """Test budget tracker initialization."""
    assert budget_tracker.daily_limit == 0.20
    assert budget_tracker.used_today == 0.0
    assert budget_tracker.cost_per_image == 0.04
    assert budget_tracker.reset_time == datetime(2023, 1, 1, 0, 0, 0)

def test_can_generate_within_budget(budget_tracker):
    """Test can_generate when within budget."""
    assert budget_tracker.can_generate() is True
    assert budget_tracker.can_generate(0.10) is True

def test_can_generate_exceeds_budget(budget_tracker):
    """Test can_generate when exceeding budget."""
    budget_tracker.used_today = 0.17
    assert budget_tracker.can_generate() is False
    assert budget_tracker.can_generate(0.10) is False

def test_record_usage_within_budget(budget_tracker):
    """Test record_usage when within budget."""
    budget_tracker.record_usage()
    assert budget_tracker.used_today == 0.04

def test_record_usage_exceeds_budget(budget_tracker):
    """Test record_usage when exceeding budget."""
    budget_tracker.used_today = 0.17
    with pytest.raises(BudgetExceededError):
        budget_tracker.record_usage()

def test_get_remaining_budget(budget_tracker):
    """Test get_remaining_budget."""
    assert budget_tracker.get_remaining_budget() == 0.20
    budget_tracker.record_usage()
    assert budget_tracker.get_remaining_budget() == 0.16

def test_check_reset_same_day(budget_tracker):
    """Test _check_reset when same day."""
    budget_tracker.used_today = 0.10
    budget_tracker._check_reset()
    assert budget_tracker.used_today == 0.10

def test_check_reset_new_day(budget_tracker):
    """Test _check_reset when new day."""
    budget_tracker.used_today = 0.10
    with patch('modules.budget_tracker.datetime') as mock_datetime:
        # Set current time to next day
        mock_datetime.now.return_value = datetime(2023, 1, 2, 12, 0, 0)
        budget_tracker._check_reset()
        assert budget_tracker.used_today == 0.0

def test_save_state(budget_tracker):
    """Test _save_state."""
    mock_file = mock_open()
    with patch('builtins.open', mock_file):
        budget_tracker.used_today = 0.10
        budget_tracker._save_state()
        mock_file.assert_called_once_with("dalle_budget_state.json", "w")
        # Check that json.dump was called with correct data
        args, _ = mock_file().write.call_args
        saved_data = json.loads(args[0])
        assert saved_data["used_today"] == 0.10

def test_load_state_same_day(budget_tracker):
    """Test _load_state when same day."""
    state_data = {
        "used_today": 0.15,
        "reset_time": datetime(2023, 1, 1, 0, 0, 0).isoformat(),
        "daily_limit": 0.20
    }
    mock_file = mock_open(read_data=json.dumps(state_data))
    with patch('builtins.open', mock_file):
        with patch('os.path.exists', return_value=True):
            budget_tracker._load_state()
            assert budget_tracker.used_today == 0.15

def test_load_state_different_day(budget_tracker):
    """Test _load_state when different day."""
    state_data = {
        "used_today": 0.15,
        "reset_time": datetime(2022, 12, 31, 0, 0, 0).isoformat(),
        "daily_limit": 0.20
    }
    mock_file = mock_open(read_data=json.dumps(state_data))
    with patch('builtins.open', mock_file):
        with patch('os.path.exists', return_value=True):
            budget_tracker._load_state()
            assert budget_tracker.used_today == 0.0  # Should not load old data 