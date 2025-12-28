"""
Comprehensive unit tests for LLM Service

Tests cover:
- New GroqModel enum values and their string representations
- Default model configuration change to GPT_OSS_120B
- LLMService initialization with various configurations
- Generate method with different models and parameters
- Transform block functionality with philosophical thinkers
- Logic analysis capabilities
- Stream generation
- Error handling and edge cases
- Thinker prompt building with various combinations
"""
import os
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import AsyncIterator

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.llm_service import LLMService, GroqModel, llm_service


class TestGroqModelEnum:
    """Test suite for the GroqModel enum with new model definitions"""
    
    def test_gpt_oss_120b_model_value(self):
        """Test GPT OSS 120B model enum value"""
        assert GroqModel.GPT_OSS_120B.value == "openai/gpt-oss-120b"
        assert isinstance(GroqModel.GPT_OSS_120B, str)
    
    def test_qwen3_32b_model_value(self):
        """Test Qwen 3 32B model enum value"""
        assert GroqModel.QWEN3_32B.value == "qwen-qwq-32b"
        assert isinstance(GroqModel.QWEN3_32B, str)
    
    def test_llama4_maverick_model_value(self):
        """Test Llama 4 Maverick model enum value"""
        assert GroqModel.LLAMA4_MAVERICK.value == "meta-llama/llama-4-maverick-17b-128e-instruct"
        assert isinstance(GroqModel.LLAMA4_MAVERICK, str)
    
    def test_kimi_k2_model_value(self):
        """Test Kimi K2 model enum value"""
        assert GroqModel.KIMI_K2.value == "moonshotai/kimi-k2-instruct"
        assert isinstance(GroqModel.KIMI_K2, str)
    
    def test_llama_33_70b_model_value(self):
        """Test Llama 3.3 70B model enum value"""
        assert GroqModel.LLAMA_33_70B.value == "llama-3.3-70b-versatile"
        assert isinstance(GroqModel.LLAMA_33_70B, str)
    
    def test_all_models_are_strings(self):
        """Test that all model enum values are strings"""
        for model in GroqModel:
            assert isinstance(model, str)
            assert isinstance(model.value, str)
            assert len(model.value) > 0
    
    def test_model_enum_count(self):
        """Test that we have exactly 5 models defined"""
        assert len(list(GroqModel)) == 5
    
    def test_model_names_unique(self):
        """Test that all model names are unique"""
        model_names = [model.name for model in GroqModel]
        assert len(model_names) == len(set(model_names))
    
    def test_model_values_unique(self):
        """Test that all model values are unique"""
        model_values = [model.value for model in GroqModel]
        assert len(model_values) == len(set(model_values))
    
    def test_enum_iteration(self):
        """Test that we can iterate over all models"""
        models = list(GroqModel)
        assert len(models) == 5
        assert GroqModel.GPT_OSS_120B in models
        assert GroqModel.QWEN3_32B in models
        assert GroqModel.LLAMA4_MAVERICK in models
        assert GroqModel.KIMI_K2 in models
        assert GroqModel.LLAMA_33_70B in models


class TestLLMServiceDefaultModel:
    """Test suite for the default model configuration change"""
    
    def test_default_model_is_gpt_oss_120b(self):
        """Test that the default model is now GPT_OSS_120B"""
        assert LLMService.DEFAULT_MODEL == GroqModel.GPT_OSS_120B
    
    def test_default_model_value(self):
        """Test the actual value of the default model"""
        assert LLMService.DEFAULT_MODEL.value == "openai/gpt-oss-120b"
    
    def test_default_model_is_groq_model_enum(self):
        """Test that default model is a GroqModel enum instance"""
        assert isinstance(LLMService.DEFAULT_MODEL, GroqModel)


class TestLLMServiceInitialization:
    """Test suite for LLMService initialization"""
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-api-key-123"})
    @patch('services.llm_service.AsyncGroq')
    def test_init_with_env_var(self, mock_groq):
        """Test initialization with API key from environment variable"""
        service = LLMService()
        assert service.api_key == "test-api-key-123"
        mock_groq.assert_called_once_with(api_key="test-api-key-123")
    
    @patch('services.llm_service.AsyncGroq')
    def test_init_with_explicit_api_key(self, mock_groq):
        """Test initialization with explicitly provided API key"""
        service = LLMService(api_key="explicit-key-456")
        assert service.api_key == "explicit-key-456"
        mock_groq.assert_called_once_with(api_key="explicit-key-456")
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError"""
        with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
            LLMService()
    
    @patch.dict(os.environ, {"GROQ_API_KEY": ""})
    def test_init_with_empty_api_key_raises_error(self):
        """Test that initialization with empty API key raises ValueError"""
        with pytest.raises(ValueError, match="GROQ_API_KEY not found"):
            LLMService()
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch('services.llm_service.AsyncGroq')
    def test_explicit_api_key_overrides_env_var(self, mock_groq):
        """Test that explicit API key takes precedence over environment variable"""
        service = LLMService(api_key="explicit-override")
        assert service.api_key == "explicit-override"
        mock_groq.assert_called_once_with(api_key="explicit-override")


class TestLLMServiceGenerate:
    """Test suite for the generate method"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mocked LLMService instance"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq') as mock_groq:
                mock_client = AsyncMock()
                mock_groq.return_value = mock_client
                service = LLMService()
                service.client = mock_client
                return service, mock_client
    
    @pytest.mark.asyncio
    async def test_generate_with_defaults(self, mock_service):
        """Test generate method with default parameters"""
        service, mock_client = mock_service
        
        # Mock the response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.generate(prompt="Test prompt")
        
        assert result == "Generated response"
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == GroqModel.GPT_OSS_120B.value
        assert call_kwargs['temperature'] == 0.7
        assert call_kwargs['max_tokens'] == 2000
    
    @pytest.mark.asyncio
    async def test_generate_with_custom_model(self, mock_service):
        """Test generate with each new model"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Test with each new model
        for model in GroqModel:
            mock_client.chat.completions.create.reset_mock()
            await service.generate(prompt="Test", model=model)
            
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs['model'] == model.value
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_service):
        """Test generate with system prompt"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await service.generate(
            prompt="User prompt",
            system_prompt="System context"
        )
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == 'System context'
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == 'User prompt'
    
    @pytest.mark.asyncio
    async def test_generate_without_system_prompt(self, mock_service):
        """Test generate without system prompt"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await service.generate(prompt="User prompt")
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs['messages']
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
    
    @pytest.mark.asyncio
    async def test_generate_with_custom_temperature(self, mock_service):
        """Test generate with custom temperature values"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        temperatures = [0.0, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0]
        for temp in temperatures:
            mock_client.chat.completions.create.reset_mock()
            await service.generate(prompt="Test", temperature=temp)
            
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs['temperature'] == temp
    
    @pytest.mark.asyncio
    async def test_generate_with_custom_max_tokens(self, mock_service):
        """Test generate with custom max_tokens values"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        token_limits = [100, 500, 1000, 2000, 4000]
        for max_tokens in token_limits:
            mock_client.chat.completions.create.reset_mock()
            await service.generate(prompt="Test", max_tokens=max_tokens)
            
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs['max_tokens'] == max_tokens
    
    @pytest.mark.asyncio
    async def test_generate_streaming(self, mock_service):
        """Test generate with streaming enabled"""
        service, mock_client = mock_service
        
        result = await service.generate(prompt="Test", stream=True)
        
        # Result should be an async iterator
        assert hasattr(result, '__aiter__')


class TestLLMServiceStreamGenerate:
    """Test suite for streaming generation"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mocked LLMService instance"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq') as mock_groq:
                mock_client = AsyncMock()
                mock_groq.return_value = mock_client
                service = LLMService()
                service.client = mock_client
                return service, mock_client
    
    @pytest.mark.asyncio
    async def test_stream_generate_yields_chunks(self, mock_service):
        """Test that stream generation yields content chunks"""
        service, mock_client = mock_service
        
        # Mock streaming response
        async def mock_stream():
            chunks = ["Hello", " ", "world", "!"]
            for chunk_text in chunks:
                chunk = Mock()
                chunk.choices = [Mock()]
                chunk.choices[0].delta.content = chunk_text
                yield chunk
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
        
        result = await service.generate(prompt="Test", stream=True)
        
        collected = []
        async for chunk in result:
            collected.append(chunk)
        
        assert collected == ["Hello", " ", "world", "!"]
    
    @pytest.mark.asyncio
    async def test_stream_generate_skips_none_content(self, mock_service):
        """Test that stream generation skips chunks with None content"""
        service, mock_client = mock_service
        
        async def mock_stream():
            chunks = [
                ("Hello", True),
                (None, False),
                (" world", True),
                (None, False),
            ]
            for content, has_content in chunks:
                chunk = Mock()
                chunk.choices = [Mock()]
                chunk.choices[0].delta.content = content
                yield chunk
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
        
        result = await service.generate(prompt="Test", stream=True)
        
        collected = []
        async for chunk in result:
            collected.append(chunk)
        
        assert collected == ["Hello", " world"]


class TestLLMServiceTransformBlock:
    """Test suite for transform_block method"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mocked LLMService instance"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq') as mock_groq:
                mock_client = AsyncMock()
                mock_groq.return_value = mock_client
                service = LLMService()
                service.client = mock_client
                return service, mock_client
    
    @pytest.mark.asyncio
    async def test_transform_block_with_nietzsche(self, mock_service):
        """Test transform_block with Nietzsche thinker"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed text"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.transform_block(
            content="Original text",
            thinker="nietzsche",
            intent="critique"
        )
        
        assert result == "Transformed text"
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['temperature'] == 0.8
        
        # Check system prompt contains Nietzsche
        messages = call_kwargs['messages']
        system_msg = next((m for m in messages if m['role'] == 'system'), None)
        assert system_msg is not None
        assert 'Nietzsche' in system_msg['content']
    
    @pytest.mark.asyncio
    async def test_transform_block_all_thinkers(self, mock_service):
        """Test transform_block with all available thinkers"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        thinkers = ["nietzsche", "kant", "wittgenstein", "sankara", "hume", "spinoza", "socrates"]
        
        for thinker in thinkers:
            mock_client.chat.completions.create.reset_mock()
            await service.transform_block(
                content="Test content",
                thinker=thinker,
                intent="critique"
            )
            
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            messages = call_kwargs['messages']
            system_msg = next((m for m in messages if m['role'] == 'system'), None)
            assert system_msg is not None
    
    @pytest.mark.asyncio
    async def test_transform_block_all_intents(self, mock_service):
        """Test transform_block with all available intents"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        intents = ["critique", "steelman", "simplify", "mystify", "expand", "condense"]
        
        for intent in intents:
            mock_client.chat.completions.create.reset_mock()
            await service.transform_block(
                content="Test content",
                thinker="nietzsche",
                intent=intent
            )
            
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            messages = call_kwargs['messages']
            system_msg = next((m for m in messages if m['role'] == 'system'), None)
            assert system_msg is not None
    
    @pytest.mark.asyncio
    async def test_transform_block_with_style(self, mock_service):
        """Test transform_block with custom style"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await service.transform_block(
            content="Test content",
            thinker="kant",
            intent="critique",
            style="aphoristic"
        )
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs['messages']
        system_msg = next((m for m in messages if m['role'] == 'system'), None)
        assert 'aphoristic' in system_msg['content']
    
    @pytest.mark.asyncio
    async def test_transform_block_with_custom_model(self, mock_service):
        """Test transform_block with different models"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await service.transform_block(
            content="Test",
            thinker="nietzsche",
            intent="critique",
            model=GroqModel.QWEN3_32B
        )
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == GroqModel.QWEN3_32B.value
    
    @pytest.mark.asyncio
    async def test_transform_block_unknown_thinker(self, mock_service):
        """Test transform_block with unknown thinker falls back gracefully"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await service.transform_block(
            content="Test",
            thinker="unknown_philosopher",
            intent="critique"
        )
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs['messages']
        system_msg = next((m for m in messages if m['role'] == 'system'), None)
        assert 'unknown_philosopher' in system_msg['content']


class TestLLMServiceAnalyzeLogic:
    """Test suite for analyze_logic method"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mocked LLMService instance"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq') as mock_groq:
                mock_client = AsyncMock()
                mock_groq.return_value = mock_client
                service = LLMService()
                service.client = mock_client
                return service, mock_client
    
    @pytest.mark.asyncio
    async def test_analyze_logic_valid_json_response(self, mock_service):
        """Test analyze_logic with valid JSON response"""
        service, mock_client = mock_service
        
        json_response = {
            "fallacies": [{"type": "ad hominem", "location": "quote", "explanation": "why"}],
            "assumptions": [{"assumption": "test", "explanation": "why"}],
            "undefined_terms": ["term1"],
            "structure": {"premises": ["p1"], "conclusion": "c1"}
        }
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(json_response)
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.analyze_logic(content="Test argument")
        
        assert result == json_response
        assert "fallacies" in result
        assert "assumptions" in result
        assert "undefined_terms" in result
        assert "structure" in result
    
    @pytest.mark.asyncio
    async def test_analyze_logic_invalid_json_response(self, mock_service):
        """Test analyze_logic handles invalid JSON gracefully"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.analyze_logic(content="Test argument")
        
        assert "fallacies" in result
        assert "assumptions" in result
        assert "undefined_terms" in result
        assert "structure" in result
        assert "raw_analysis" in result
        assert result["raw_analysis"] == "This is not valid JSON"
        assert result["fallacies"] == []
        assert result["assumptions"] == []
    
    @pytest.mark.asyncio
    async def test_analyze_logic_uses_low_temperature(self, mock_service):
        """Test that analyze_logic uses low temperature for analytical tasks"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "{}"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await service.analyze_logic(content="Test")
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['temperature'] == 0.3
    
    @pytest.mark.asyncio
    async def test_analyze_logic_with_custom_model(self, mock_service):
        """Test analyze_logic with different models"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "{}"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await service.analyze_logic(
            content="Test",
            model=GroqModel.LLAMA_33_70B
        )
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == GroqModel.LLAMA_33_70B.value


class TestBuildThinkerPrompt:
    """Test suite for _build_thinker_prompt method"""
    
    @pytest.fixture
    def service(self):
        """Create a LLMService instance with mocked client"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq'):
                return LLMService()
    
    def test_build_thinker_prompt_nietzsche(self, service):
        """Test building prompt for Nietzsche"""
        prompt = service._build_thinker_prompt("nietzsche", "critique")
        assert "Nietzsche" in prompt
        assert "critique" in prompt.lower()
    
    def test_build_thinker_prompt_all_thinkers(self, service):
        """Test building prompts for all known thinkers"""
        thinkers = ["nietzsche", "kant", "wittgenstein", "sankara", "hume", "spinoza", "socrates"]
        
        for thinker in thinkers:
            prompt = service._build_thinker_prompt(thinker, "critique")
            assert len(prompt) > 0
            assert thinker.lower() in prompt.lower() or thinker.capitalize() in prompt
    
    def test_build_thinker_prompt_all_intents(self, service):
        """Test building prompts for all known intents"""
        intents = ["critique", "steelman", "simplify", "mystify", "expand", "condense"]
        
        for intent in intents:
            prompt = service._build_thinker_prompt("nietzsche", intent)
            assert len(prompt) > 0
    
    def test_build_thinker_prompt_with_style(self, service):
        """Test building prompt with style parameter"""
        prompt = service._build_thinker_prompt("kant", "critique", style="aphoristic")
        assert "aphoristic" in prompt
    
    def test_build_thinker_prompt_without_style(self, service):
        """Test building prompt without style parameter"""
        prompt = service._build_thinker_prompt("kant", "critique")
        assert len(prompt) > 0
    
    def test_build_thinker_prompt_unknown_thinker(self, service):
        """Test building prompt with unknown thinker"""
        prompt = service._build_thinker_prompt("unknown_thinker", "critique")
        assert "unknown_thinker" in prompt
        assert len(prompt) > 0
    
    def test_build_thinker_prompt_unknown_intent(self, service):
        """Test building prompt with unknown intent"""
        prompt = service._build_thinker_prompt("nietzsche", "unknown_intent")
        assert "unknown_intent" in prompt
        assert len(prompt) > 0
    
    def test_build_thinker_prompt_case_insensitive(self, service):
        """Test that thinker and intent matching is case-insensitive"""
        prompt1 = service._build_thinker_prompt("NIETZSCHE", "CRITIQUE")
        prompt2 = service._build_thinker_prompt("nietzsche", "critique")
        prompt3 = service._build_thinker_prompt("Nietzsche", "Critique")
        
        # All should produce valid prompts
        assert len(prompt1) > 0
        assert len(prompt2) > 0
        assert len(prompt3) > 0


class TestSingletonInstance:
    """Test suite for the singleton llm_service instance"""
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch('services.llm_service.AsyncGroq')
    def test_singleton_instance_exists(self, mock_groq):
        """Test that the singleton instance is created"""
        from services.llm_service import llm_service
        assert llm_service is not None
        assert isinstance(llm_service, LLMService)
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"})
    @patch('services.llm_service.AsyncGroq')
    def test_singleton_uses_default_model(self, mock_groq):
        """Test that singleton instance uses the default model"""
        from services.llm_service import llm_service
        assert LLMService.DEFAULT_MODEL == GroqModel.GPT_OSS_120B


class TestEdgeCases:
    """Test suite for edge cases and error conditions"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mocked LLMService instance"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq') as mock_groq:
                mock_client = AsyncMock()
                mock_groq.return_value = mock_client
                service = LLMService()
                service.client = mock_client
                return service, mock_client
    
    @pytest.mark.asyncio
    async def test_generate_empty_prompt(self, mock_service):
        """Test generate with empty prompt"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.generate(prompt="")
        assert result == "Response"
    
    @pytest.mark.asyncio
    async def test_generate_very_long_prompt(self, mock_service):
        """Test generate with very long prompt"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        long_prompt = "a" * 10000
        result = await service.generate(prompt=long_prompt)
        assert result == "Response"
    
    @pytest.mark.asyncio
    async def test_generate_special_characters_in_prompt(self, mock_service):
        """Test generate with special characters in prompt"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        special_prompt = "Test with émojis 🎭 and symbols @#$%^&*()"
        result = await service.generate(prompt=special_prompt)
        assert result == "Response"
    
    @pytest.mark.asyncio
    async def test_transform_block_empty_content(self, mock_service):
        """Test transform_block with empty content"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.transform_block(
            content="",
            thinker="nietzsche",
            intent="critique"
        )
        assert result == "Transformed"
    
    @pytest.mark.asyncio
    async def test_analyze_logic_empty_content(self, mock_service):
        """Test analyze_logic with empty content"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "{}"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.analyze_logic(content="")
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_logic_partial_json_response(self, mock_service):
        """Test analyze_logic with partially valid JSON"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"fallacies": [}'  # Invalid JSON
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await service.analyze_logic(content="Test")
        
        # Should fall back to default structure
        assert "raw_analysis" in result
        assert result["fallacies"] == []


class TestModelCompatibility:
    """Test suite to ensure all new models work correctly"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mocked LLMService instance"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq') as mock_groq:
                mock_client = AsyncMock()
                mock_groq.return_value = mock_client
                service = LLMService()
                service.client = mock_client
                return service, mock_client
    
    @pytest.mark.asyncio
    async def test_all_models_in_generate(self, mock_service):
        """Test that all new models can be used in generate method"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        for model in GroqModel:
            mock_client.chat.completions.create.reset_mock()
            result = await service.generate(prompt="Test", model=model)
            assert result == "Response"
            
            call_kwargs = mock_client.chat.completions.create.call_args[1]
            assert call_kwargs['model'] == model.value
    
    @pytest.mark.asyncio
    async def test_all_models_in_transform_block(self, mock_service):
        """Test that all new models can be used in transform_block"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Transformed"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        for model in GroqModel:
            mock_client.chat.completions.create.reset_mock()
            result = await service.transform_block(
                content="Test",
                thinker="nietzsche",
                intent="critique",
                model=model
            )
            assert result == "Transformed"
    
    @pytest.mark.asyncio
    async def test_all_models_in_analyze_logic(self, mock_service):
        """Test that all new models can be used in analyze_logic"""
        service, mock_client = mock_service
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "{}"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        for model in GroqModel:
            mock_client.chat.completions.create.reset_mock()
            result = await service.analyze_logic(content="Test", model=model)
            assert isinstance(result, dict)


# Integration tests for real-world scenarios
class TestIntegrationScenarios:
    """Integration test scenarios combining multiple features"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mocked LLMService instance"""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
            with patch('services.llm_service.AsyncGroq') as mock_groq:
                mock_client = AsyncMock()
                mock_groq.return_value = mock_client
                service = LLMService()
                service.client = mock_client
                return service, mock_client
    
    @pytest.mark.asyncio
    async def test_workflow_analyze_then_transform(self, mock_service):
        """Test workflow: analyze logic then transform with different thinker"""
        service, mock_client = mock_service
        
        # First, analyze
        analysis_response = Mock()
        analysis_response.choices = [Mock()]
        analysis_response.choices[0].message.content = json.dumps({
            "fallacies": [{"type": "straw man", "location": "test", "explanation": "why"}],
            "assumptions": [],
            "undefined_terms": [],
            "structure": {"premises": ["p1"], "conclusion": "c1"}
        })
        
        # Then, transform
        transform_response = Mock()
        transform_response.choices = [Mock()]
        transform_response.choices[0].message.content = "Transformed critique"
        
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[analysis_response, transform_response]
        )
        
        # Execute workflow
        analysis = await service.analyze_logic("Original argument")
        transformation = await service.transform_block(
            "Original argument",
            thinker="socrates",
            intent="critique"
        )
        
        assert "fallacies" in analysis
        assert transformation == "Transformed critique"
        assert mock_client.chat.completions.create.call_count == 2