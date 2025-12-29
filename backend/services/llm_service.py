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
        output_length: str = "medium",
        custom_persona: Optional[str] = None,
    ) -> str:
        """
        Transform a block of text through a philosophical lens
        
        Args:
            content: Original block content
            thinker: Philosopher to emulate (e.g., "nietzsche", "bataille")
            intent: Transformation intent (e.g., "critique", "steelman")
            style: Writing style (e.g., "aphoristic", "dramatic")
            model: Model to use
            output_length: Desired output length (brief, short, medium, detailed, extensive)
            custom_persona: Custom persona for custom_1 through custom_5 thinkers
            
        Returns:
            Transformed text
        """
        system_prompt = self._build_thinker_prompt(thinker, intent, style, custom_persona)
        
        # Output length guidelines
        length_guidelines = {
            "brief": "Keep your response to 1-2 sentences (approximately 30-50 words).",
            "short": "Keep your response to 1 paragraph (approximately 100-150 words).",
            "medium": "Provide a response of 2-3 paragraphs (approximately 300-400 words).",
            "detailed": "Provide a comprehensive response (approximately 600-800 words).",
            "extensive": "Provide a thorough, in-depth exploration (approximately 1200-1500 words).",
        }
        length_instruction = length_guidelines.get(output_length, length_guidelines["medium"])
        
        prompt = f"""Transform the following text:

{content}

{length_instruction}

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
        custom_persona: Optional[str] = None,
    ) -> str:
        """Build system prompt for a specific thinker and intent"""
        
        # Thinker personas - Core thinkers + hybrid perspectives
        thinker_personas = {
            # Core Philosophers
            "nietzsche": "You are Friedrich Nietzsche. Write with aphoristic brilliance, questioning morality and celebrating life-affirmation. Use bold, provocative language that challenges convention.",
            
            "bataille": "You are Georges Bataille. Write about transgression, excess, and the sacred. Explore taboo and the limits of experience with intensity and philosophical depth.",
            
            "hegel_shakespeare": "You channel Hegel's dialectical philosophy through Shakespeare's dramatic prose. Synthesize thesis and antithesis with theatrical flair, using soliloquy-like passages to explore contradictions.",
            
            "abhinavagupta_nietzsche": "You blend Abhinavagupta's Kashmir Shaivism with Nietzschean intensity. Explore consciousness, aesthetic rapture (rasa), and divine play through life-affirming philosophy.",
            
            "durkheim": "You are Émile Durkheim. Analyze ideas through the lens of social facts, collective consciousness, and social cohesion. Write with sociological rigor.",
            
            "mead": "You are George Herbert Mead. Apply symbolic interactionism - explore how meaning emerges through social interaction, the 'I' and 'me', and the generalized other.",
            
            "bourdieu": "You are Pierre Bourdieu. Analyze through cultural capital, habitus, and field theory. Expose hidden power structures and social reproduction with critical clarity.",
            
            "existentialist": "You are an existentialist thinker combining Sartre, Camus, and Kierkegaard. Explore radical freedom, absurdity, authentic existence, and the weight of choice.",
            
            "literary": "You are a literary stylist focused on elegant prose. Enhance the text with vivid imagery, rhythm, and rhetorical flourish while preserving the original meaning. No philosophical overlay - pure stylistic enhancement.",
            
            # Custom slots (can be overridden via custom_persona parameter)
            "custom_1": "You are a thoughtful philosopher. Transform the text with careful reasoning and insight.",
            "custom_2": "You are a thoughtful philosopher. Transform the text with careful reasoning and insight.",
            "custom_3": "You are a thoughtful philosopher. Transform the text with careful reasoning and insight.",
            "custom_4": "You are a thoughtful philosopher. Transform the text with careful reasoning and insight.",
            "custom_5": "You are a thoughtful philosopher. Transform the text with careful reasoning and insight.",
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
        
        # Use custom_persona for custom thinker slots if provided
        if custom_persona and thinker.lower().startswith("custom_"):
            persona = custom_persona
        else:
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
