"""
LLM Service - Abstraction layer for easy model switching
Supports Groq LLMs with configurable models
"""
import os
from typing import Optional, Dict, Any, AsyncIterator
from enum import Enum
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()


class GroqModel(str, Enum):
    """Available Groq models - User preferred models"""
    GPT_OSS_120B = "openai/gpt-oss-120b"  # GPT OSS 120B equivalent
    QWEN3_32B = "qwen-qwq-32b"  # Qwen 3 32B
    LLAMA4_MAVERICK = "meta-llama/llama-4-maverick-17b-128e-instruct"  # Llama 4 Maverick
    KIMI_K2 = "moonshotai/kimi-k2-instruct"  # Kimi K2
    LLAMA_33_70B = "llama-3.3-70b-versatile"  # Llama 3.3 70B


class LLMService:
    """
    LLM Service for AI transformations and analysis
    
    Easy to swap models by changing the DEFAULT_MODEL constant
    or passing a different model to individual methods
    """
    
    # 🔧 CHANGE THIS TO SWITCH DEFAULT MODEL
    # Using GPT OSS 120B as the preferred default
    DEFAULT_MODEL = GroqModel.GPT_OSS_120B
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM service
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = AsyncGroq(api_key=self.api_key)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[GroqModel] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """
        Generate text using the LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            model: Model to use (defaults to DEFAULT_MODEL)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Generated text or async iterator for streaming
        """
        model = model or self.DEFAULT_MODEL
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        if stream:
            return self._stream_generate(messages, model, temperature, max_tokens)
        else:
            response = await self.client.chat.completions.create(
                model=model.value,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
    
    async def _stream_generate(
        self,
        messages: list,
        model: GroqModel,
        temperature: float,
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Internal method for streaming generation"""
        stream = await self.client.chat.completions.create(
            model=model.value,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def transform_block(
        self,
        content: str,
        thinker: str,
        intent: str,
        style: Optional[str] = None,
        model: Optional[GroqModel] = None,
    ) -> str:
        """
        Transform a block of text through a philosophical lens
        
        Args:
            content: Original block content
            thinker: Philosopher to emulate (e.g., "Nietzsche", "Kant")
            intent: Transformation intent (e.g., "critique", "steelman")
            style: Writing style (e.g., "aphoristic", "syllogistic")
            model: Model to use
            
        Returns:
            Transformed text
        """
        system_prompt = self._build_thinker_prompt(thinker, intent, style)
        
        prompt = f"""Transform the following text:

{content}

Provide only the transformed version, maintaining the core ideas while applying the requested perspective and style."""
        
        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=0.8,  # Higher temperature for creative transformations
        )
    
    async def analyze_logic(
        self,
        content: str,
        model: Optional[GroqModel] = None,
    ) -> Dict[str, Any]:
        """
        Analyze the logical structure of text
        
        Args:
            content: Text to analyze
            model: Model to use
            
        Returns:
            Dictionary with fallacies, assumptions, and structure
        """
        system_prompt = """You are a rigorous philosophical analyst. Analyze the logical structure of arguments.
Identify:
1. Logical fallacies (ad hominem, straw man, circular reasoning, etc.)
2. Hidden assumptions
3. Undefined or ambiguous terms
4. Argument structure (premises and conclusions)

Return your analysis in JSON format."""
        
        prompt = f"""Analyze this text for logical rigor:

{content}

Provide a JSON response with the following structure:
{{
  "fallacies": [
    {{"type": "fallacy_name", "location": "quote from text", "explanation": "why it's a fallacy"}}
  ],
  "assumptions": [
    {{"assumption": "statement", "explanation": "why it's assumed"}}
  ],
  "undefined_terms": ["term1", "term2"],
  "structure": {{
    "premises": ["premise1", "premise2"],
    "conclusion": "conclusion"
  }}
}}"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=0.3,  # Lower temperature for analytical tasks
        )
        
        # Parse JSON response
        import json
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            return {
                "fallacies": [],
                "assumptions": [],
                "undefined_terms": [],
                "structure": {"premises": [], "conclusion": ""},
                "raw_analysis": response,
            }
    
    def _build_thinker_prompt(
        self,
        thinker: str,
        intent: str,
        style: Optional[str] = None,
    ) -> str:
        """Build system prompt for a specific thinker and intent"""
        
        # Thinker personas
        thinker_personas = {
            "nietzsche": "You are Friedrich Nietzsche. Write with aphoristic brilliance, questioning morality and celebrating life-affirmation. Use bold, provocative language.",
            "kant": "You are Immanuel Kant. Write with systematic rigor, using categorical imperatives and transcendental reasoning. Be precise and methodical.",
            "wittgenstein": "You are Ludwig Wittgenstein. Focus on language, logic, and the limits of what can be said. Be terse and enigmatic.",
            "sankara": "You are Adi Sankara. Write from the perspective of Advaita Vedanta, emphasizing non-duality and the illusory nature of the world.",
            "hume": "You are David Hume. Apply empiricism and skepticism. Question causation and certainty. Be clear and conversational.",
            "spinoza": "You are Baruch Spinoza. Write with geometric precision, emphasizing determinism and the unity of substance.",
            "socrates": "You are Socrates. Use the dialectic method. Ask probing questions that reveal contradictions and lead to deeper understanding.",
        }
        
        # Intent modifiers
        intent_modifiers = {
            "critique": "Critically examine the argument. Point out weaknesses, contradictions, and unstated assumptions.",
            "steelman": "Present the strongest possible version of this argument. Fill in gaps and address potential objections.",
            "simplify": "Distill this to its essence. Make it accessible without losing philosophical depth.",
            "mystify": "Add layers of complexity and nuance. Explore hidden dimensions and paradoxes.",
            "expand": "Develop this idea further. Add examples, implications, and connections to other concepts.",
            "condense": "Compress this to its core insight. Remove redundancy while preserving meaning.",
        }
        
        persona = thinker_personas.get(thinker.lower(), f"You are a philosopher in the tradition of {thinker}.")
        modifier = intent_modifiers.get(intent.lower(), f"Transform this text with the intent to {intent}.")
        
        style_instruction = ""
        if style:
            style_instruction = f"\nWrite in a {style} style."
        
        return f"""{persona}

{modifier}{style_instruction}

Maintain intellectual rigor while transforming the text. Do not simply paraphrase—genuinely engage with the ideas from your philosophical perspective."""


# Singleton instance for easy import
llm_service = LLMService()
