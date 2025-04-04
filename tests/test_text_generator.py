import pytest
from unittest.mock import patch, MagicMock
from modules.text_generator import OpenAICostManager, GPT35TextGenerator

@pytest.fixture
def cost_manager():
    return OpenAICostManager()

@pytest.fixture
def text_generator(cost_manager):
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        return GPT35TextGenerator(cost_manager)

class TestOpenAICostManager:
    def test_initialization(self, cost_manager):
        assert cost_manager.monthly_budget == 10.00
        assert cost_manager.used_cost == 0.0
        assert cost_manager.gpt35_price == 0.002/1000

    def test_can_make_call_within_budget(self, cost_manager):
        assert cost_manager.can_make_call(1000) is True  # Should cost $0.002

    def test_can_make_call_exceeds_budget(self, cost_manager):
        cost_manager.used_cost = 9.99
        assert cost_manager.can_make_call(1000) is False

    def test_track_usage(self, cost_manager):
        cost_manager.track_usage(1000)  # Should cost $0.002
        assert cost_manager.used_cost == 0.002

class TestGPT35TextGenerator:
    def test_initialization(self, text_generator):
        assert text_generator.openai_api_key == 'test-key'
        assert text_generator.cost_manager is not None
        assert len(text_generator.template_overrides) == 3

    @patch('openai.OpenAI')
    def test_generate_text_success(self, mock_openai, text_generator):
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="Test response"))
        ]
        mock_completion.usage = MagicMock(total_tokens=50)
        mock_client.chat.completions.create.return_value = mock_completion
        text_generator.client = mock_client

        context = {
            'product': 'test product',
            'category': 'skincare',
            'key_benefit': 'hydration',
            'style': 'conversational',
            'trend': 'glass skin'
        }

        result = text_generator.generate_text('captions', context)
        assert result == "Test response"
        assert text_generator.cost_manager.used_cost > 0

    def test_generate_text_budget_exceeded(self, text_generator):
        text_generator.cost_manager.used_cost = 10.00  # Max budget
        
        context = {
            'product': 'test product',
            'category': 'skincare',
            'key_benefit': 'hydration',
            'trend': 'glass skin'
        }

        result = text_generator.generate_text('captions', context)
        assert result == text_generator._fallback_response('captions', context)

    @patch('openai.OpenAI')
    def test_generate_text_api_error(self, mock_openai, text_generator):
        # Mock API error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        text_generator.client = mock_client

        context = {
            'product': 'test product',
            'category': 'skincare',
            'key_benefit': 'hydration',
            'trend': 'glass skin'
        }

        result = text_generator.generate_text('captions', context)
        assert result == text_generator._fallback_response('captions', context)

    def test_fallback_responses(self, text_generator):
        context = {
            'product': 'test serum',
            'key_benefit': 'hydration',
            'category': 'skincare',
            'trend': 'glass skin'
        }

        # Test each task type
        for task_type in ['benefits', 'captions', 'hashtags']:
            result = text_generator._fallback_response(task_type, context)
            assert result != ""
            assert isinstance(result, str)

    def test_prompt_templates(self, text_generator):
        # Verify all prompt templates exist and are properly formatted
        for template_name in ['benefits', 'captions', 'hashtags']:
            template = text_generator.template_overrides[template_name]
            assert template != ""
            assert isinstance(template, str)
            assert "{" in template and "}" in template  # Has format placeholders 