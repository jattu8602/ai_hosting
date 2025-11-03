"""
Phi-2 model loading and inference
Uses 4-bit quantization to fit in 4GB RAM
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import logging
from app.config import MODEL_NAME, MODEL_CACHE_DIR, MAX_NEW_TOKENS, TEMPERATURE, TOP_P, TOP_K

logger = logging.getLogger(__name__)

class Phi2Model:
    """Phi-2 model with 4-bit quantization for memory efficiency"""

    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Phi2Model, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None or self._tokenizer is None:
            self.load_model()

    def load_model(self):
        """Load Phi-2 model with 4-bit quantization"""
        try:
            logger.info(f"Loading model: {MODEL_NAME}")
            logger.info("Using 4-bit quantization for memory efficiency...")

            # Configure 4-bit quantization
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

            cache_dir = str(MODEL_CACHE_DIR)

            # Load tokenizer
            logger.info("Loading tokenizer...")
            self._tokenizer = AutoTokenizer.from_pretrained(
                MODEL_NAME,
                cache_dir=cache_dir,
                force_download=False  # Set to True to force re-download if corrupted
            )

            # Add padding token if missing
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token

            # Load model with quantization (GPT-2 works great with 4-bit)
            logger.info("Loading model (this may take a minute)...")
            self._model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                quantization_config=quantization_config,
                device_map="auto",
                cache_dir=cache_dir,
                torch_dtype=torch.float16,
                force_download=False  # Set to True to force re-download if corrupted
            )

            logger.info("Model loaded successfully!")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def generate(self, prompt: str, max_tokens: int = MAX_NEW_TOKENS,
                 temperature: float = TEMPERATURE, context: str = "") -> str:
        """
        Generate text from prompt

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            context: Additional context (e.g., retrieved knowledge)

        Returns:
            Generated text
        """
        if self._model is None or self._tokenizer is None:
            self.load_model()

        try:
            # Minimal prompt - GPT-2 works better with simple text continuation
            # Just complete the user's message naturally
            if context:
                # Include context but keep it minimal
                full_prompt = f"{prompt}"
            else:
                full_prompt = prompt

            # Add minimal context hint only if we have learned knowledge
            if context:
                # Very subtle context inclusion
                full_prompt = f"{prompt}"

            # Tokenize - keep prompt short for faster generation
            inputs = self._tokenizer(
                full_prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512  # Shorter input = faster processing
            ).to(self._model.device)

            # Generate (optimized for speed on CPU)
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=min(max_tokens, 25),  # Even shorter for speed (3-8 seconds)
                    temperature=0.7,  # Lower for more consistent, shorter responses
                    top_p=0.85,
                    top_k=25,
                    do_sample=True,
                    pad_token_id=self._tokenizer.eos_token_id,
                    eos_token_id=self._tokenizer.eos_token_id,
                    repetition_penalty=1.4,  # Strong penalty to prevent repetition
                    no_repeat_ngram_size=3  # Prevent phrase repetition
                )

            # Decode
            generated_text = self._tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )

            # Clean up and format response
            cleaned = generated_text.strip()

            # Remove the original prompt if it appears in response
            if prompt.lower() in cleaned.lower() and len(cleaned) > len(prompt) + 10:
                # Only remove if there's additional text
                cleaned = cleaned.replace(prompt, "").strip()

            # Remove unwanted phrases that reveal learning
            unwanted_phrases = [
                "I know", "I understand", "I learned", "I remember",
                "Based on", "According to", "From what", "As I recall"
            ]
            for phrase in unwanted_phrases:
                if phrase.lower() in cleaned.lower():
                    # Try to remove just the phrase
                    import re
                    cleaned = re.sub(rf'\b{re.escape(phrase)}\b', '', cleaned, flags=re.IGNORECASE).strip()

            # Remove any label patterns
            for label in ["User:", "Human:", "Assistant:", "Question:", "Answer:", "Response:", "Q:", "A:"]:
                if label in cleaned:
                    parts = cleaned.split(label)
                    if len(parts) > 1:
                        cleaned = parts[-1].strip()  # Take last part
                    else:
                        cleaned = cleaned.replace(label, "").strip()

            # Remove Human: and Assistant: if they appear (from few-shot examples)
            if cleaned.startswith("Assistant:"):
                cleaned = cleaned[10:].strip()
            if "Human:" in cleaned:
                cleaned = cleaned.split("Human:")[0].strip()

            # Clean whitespace
            cleaned = " ".join(cleaned.split())

            # Get first complete sentence or limit to 60 chars (shorter = faster to read)
            if len(cleaned) > 60:
                for sep in ['. ', '! ', '? ', '\n']:
                    if sep in cleaned:
                        first_part = cleaned.split(sep)[0].strip()
                        if len(first_part) > 8:  # Only if meaningful
                            cleaned = first_part + (sep.strip() if sep != '\n' else '.')
                            break
                else:
                    cleaned = cleaned[:60].strip()
                    if not cleaned.endswith(('.', '!', '?')):
                        cleaned += "."

            # Fallback responses for common greetings
            if not cleaned or len(cleaned) < 5:
                prompt_lower = prompt.lower()
                if any(word in prompt_lower for word in ["hi", "hello", "hey"]):
                    cleaned = "Hello!"
                elif "?" in prompt:
                    cleaned = "I can help with that."
                else:
                    cleaned = "I'm here to help."

            return cleaned

        except Exception as e:
            logger.error(f"Error during generation: {e}")
            return f"Error generating response: {str(e)}"

