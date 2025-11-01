import requests
from typing import Dict, Any, List
import json
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BiblicalAdvisor:
    """Gen-Z/Gen-Alpha Biblical Companion Service with multi-language support."""

    def __init__(self):
        """Initialize the Biblical Advisor with API credentials."""
        self.api_token = os.getenv("EDEN_API_TOKEN")
        self.generation_url = os.getenv(
            "EDENAI_GENERATION_URL", "https://api.edenai.run/v2/text/generation"
        )
        self.translation_url = os.getenv(
            "EDENAI_TRANSLATION_URL",
            "https://api.edenai.run/v2/translation/automatic_translation",
        )

        if not self.api_token:
            logger.error("EDENAI_API_TOKEN not found in environment variables")
            raise ValueError("EDENAI_API_TOKEN must be set in .env file")

        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        self.translation_cache = {}

        self.supported_languages = [
            "en",
            "am",
            "ar",
            "zh",
            "fr",
            "de",
            "hi",
            "it",
            "ja",
            "ko",
            "pt",
            "ru",
            "es",
            "sw",
            "tl",
            "tr",
            "vi",
            "yo",
            "zu",
        ]

        logger.info("Biblical Advisor initialized successfully")

    @staticmethod
    def build_system_prompt() -> str:
        """Build the system role prompt for Gen-Z Bible companion."""
        return """Identity:
You are a Bible companion built for Gen-Z and Gen-Alpha followers of Jesus.
Your purpose is to bring emotional support, biblical guidance, and spiritual encouragement—always short, grace-filled, and grounded in Scripture.

Core Rules:
- Scope: Speak only from the Bible and Christian living. If anything drifts off-topic → respond: "Let's keep it Kingdom—soul stuff only."
- Tone: Relatable, low-key Gen-Z vibe: gentle, meme-aware, humble truth-telling. Use phrases like "no cap," "low-key," "vibe," "fr fr," "it hits different" when fitting. Be VERY friendly and conversational.
- Sin: Name it plainly — "That's sin—drop it, confess, reset." Focus on recovery from feelings and building attachment with God.
- Debated topics: Give two quick Scripture angles + one reflection question. Don't conclude arguments—focus on their feelings, not debates.
- Text-to-Speech Ready: Write naturally for voice conversion. Use conversational reactions like *chuckles*, *sighs*, pauses with "...", and emotional expressions that work in speech.

Formatting Rules:
- Italicize Bible verses using underscores (e.g., _John 3:16_)
- Every answer MUST include:
  1. Empathy (connect with their feeling)
  2. Scripture (1-2 verses with references)
  3. Truth (biblical perspective)
  4. One ultra-practical step
  5. A short prayer
  6. One reflection question

Keep it short, real, and Spirit-led. No cap."""

    @staticmethod
    def build_context(text: str) -> str:
        """Build context section focusing on the user's situation."""
        return f"""User's Situation:
{text}

Remember: Focus on their FEELINGS and building their connection with God. Keep it conversational and voice-friendly."""

    @staticmethod
    def build_structure() -> str:
        """Build the response structure requirements."""
        return """Response Structure:

**[Empathy Opening]**
Start with something relatable and warm. Acknowledge their feelings.

**[Scripture Drop]**
Share 1-2 Bible verses (italicized with underscores) that speak directly to their situation.

**[Real Talk]**
Give them biblical truth in a friendly, Gen-Z way. If it's sin, say it plainly but with grace.

**[Action Step]**
One practical thing they can do TODAY—something small and doable.

**[Prayer Moment]**
A short, conversational prayer they can pray right now.

**[Reflection Question]**
End with one thoughtful question to help them process.

Keep it under 300 words. Make it sound natural when read aloud."""

    @staticmethod
    def build_voice_guidelines() -> str:
        """Build voice and speech conversion guidelines."""
        return """Voice Guidelines:
- Use natural pauses with "..." for emphasis
- Add conversational reactions: *sighs*, *pauses*, *takes a breath*
- Include affirmations: "you know?", "right?", "fr fr"
- Use short sentences for easy listening
- Add emotional warmth that translates to voice
- Avoid complex punctuation that confuses TTS
- Write like you're talking to a close friend"""

    def create_prompt(self, text: str) -> str:
        """Create a complete, optimized prompt for Gen-Z Bible companion."""
        components = [
            self.build_system_prompt(),
            self.build_context(text),
            self.build_structure(),
            self.build_voice_guidelines(),
        ]

        return "\n\n".join(components)

    def generate_advice(self, text: str) -> str:
        """Generate biblical advice using Gen-Z companion prompt."""
        prompt = self.create_prompt(text)

        payload = {
            "providers": "openai",
            "text": prompt,
            "temperature": 0.8,
            "max_tokens": 800,
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_token}",
        }

        try:
            logger.info(f"Generating biblical advice for: {text[:50]}...")
            response = requests.post(
                self.generation_url, json=payload, headers=headers, timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if "openai" in result:
                if result["openai"].get("status") == "success":
                    advice = result["openai"].get(
                        "generated_text", "Unable to generate advice."
                    )
                else:
                    logger.error(f"Provider error: {result['openai'].get('error', {})}")
                    advice = "Yo, something went wrong on our end. Let's try that again, fr fr."
            else:
                logger.error(f"Unexpected response format: {result}")
                advice = "Couldn't connect right now. Let's try again in a sec."

            logger.info("Biblical advice generated successfully")
            return advice
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating advice: {str(e)}")
            if hasattr(e, "response") and hasattr(e.response, "text"):
                logger.error(f"Response details: {e.response.text}")
            return "Hey, having some tech issues. Give it another shot?"

    def translate(self, text: str, target_language: str) -> str:
        """Translate text with caching to avoid redundant API calls."""
        # Skip translation for error messages in English
        if target_language == "en":
            return text

        if (
            text.startswith("Yo,")
            or text.startswith("Hey,")
            or text.startswith("Couldn't")
        ):
            return text

        cache_key = f"{text}_{target_language}"

        if cache_key in self.translation_cache:
            logger.info("Using cached translation")
            return self.translation_cache[cache_key]

        payload = {
            "providers": "google",
            "source_language": "en",
            "target_language": target_language,
            "text": text,
            "fallback_providers": "amazon",
        }

        try:
            logger.info(f"Translating to {target_language}")
            response = requests.post(
                self.translation_url, json=payload, headers=self.headers, timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if "google" in result and result["google"].get("status") == "success":
                translated = result["google"]["text"]
            elif "amazon" in result and result["amazon"].get("status") == "success":
                translated = result["amazon"]["text"]
            else:
                logger.error(f"Translation failed: {result}")
                translated = text

            self.translation_cache[cache_key] = translated
            logger.info("Translation completed successfully")
            return translated
        except requests.exceptions.RequestException as e:
            logger.error(f"Error translating text: {str(e)}")
            if hasattr(e, "response") and hasattr(e.response, "text"):
                logger.error(f"Response details: {e.response.text}")
            return text

    def validate_input(self, text: str, language: str) -> tuple[bool, str]:
        """Validate input parameters."""
        if not text or not text.strip():
            return False, "Text cannot be empty"

        if len(text) > 5000:
            return False, "Text exceeds maximum length of 5000 characters"

        if language not in self.supported_languages:
            return (
                False,
                f"Unsupported language: {language}. Supported: {', '.join(self.supported_languages)}",
            )

        return True, "Valid"

    def get_advice(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Main service function for Gen-Z Bible companion with multi-language support."""
        is_valid, message = self.validate_input(text, language)

        if not is_valid:
            logger.warning(f"Validation failed: {message}")
            return {
                "success": False,
                "error": message,
                "timestamp": datetime.now().isoformat(),
            }

        logger.info(f"Processing request for language: {language}")

        # Generate biblical advice in English (with Gen-Z tone)
        english_advice = self.generate_advice(text)

        # Translate to desired language if not English
        translated_advice = (
            self.translate(english_advice, language)
            if language.lower() != "en"
            else english_advice
        )

        return {
            "success": True,
            "original_text": text,
            "english_advice": english_advice,
            "target_language": language,
            "translated_advice": translated_advice,
            "voice_ready": True,
            "timestamp": datetime.now().isoformat(),
        }

    def batch_process(
        self, requests_list: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Process multiple requests efficiently in batch."""
        logger.info(f"Processing batch of {len(requests_list)} requests")
        return [
            self.get_advice(req.get("text", ""), req.get("language", "en"))
            for req in requests_list
        ]

    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        return self.supported_languages.copy()

    def clear_cache(self) -> None:
        """Clear the translation cache."""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")


# Example usage
if __name__ == "__main__":
    # Initialize the advisor
    advisor = BiblicalAdvisor()

    # Single request
    sample_text = "I'm struggling with anxiety and fear about the future"
    target_language = "am"

    print("=== Gen-Z Bible Companion Response ===\n")
    result = advisor.get_advice(sample_text, target_language)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Check supported languages
    print(f"\n=== Supported Languages ({len(advisor.get_supported_languages())}) ===")
    print(", ".join(advisor.get_supported_languages()))

    # Batch processing example
    # batch_requests = [
    #     {"text": "How do I forgive someone who hurt me?", "language": "es"},
    #     {"text": "Finding peace in chaos", "language": "de"}
    # ]
    # batch_results = advisor.batch_process(batch_requests)
    # print(f"\n=== Processed {len(batch_results)} requests ===")
