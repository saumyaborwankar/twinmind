from typing import List, Dict, Any, Optional, Iterator
from openai import OpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based question answering and text generation."""

    def __init__(self):
        """Initialize the LLM service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    def generate_answer(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate an answer to a question using retrieved context.

        Args:
            question: User's question
            context: Retrieved context from documents
            system_prompt: Optional system prompt to guide the LLM
            conversation_history: Optional conversation history for context

        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Build messages
            messages = []

            # Add system prompt
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system",
                    "content": self._get_default_system_prompt()
                })

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current question with context
            user_message = self._format_user_message(question, context)
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer = response.choices[0].message.content

            # Extract usage information
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            logger.info(f"Generated answer with {usage['total_tokens']} tokens")

            return {
                "answer": answer,
                "model": self.model,
                "usage": usage,
                "finish_reason": response.choices[0].finish_reason
            }

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def generate_answer_stream(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Iterator[str]:
        """
        Generate an answer with streaming response.

        Args:
            question: User's question
            context: Retrieved context from documents
            system_prompt: Optional system prompt
            conversation_history: Optional conversation history

        Yields:
            Chunks of the generated answer
        """
        try:
            # Build messages
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system",
                    "content": self._get_default_system_prompt()
                })

            if conversation_history:
                messages.extend(conversation_history)

            user_message = self._format_user_message(question, context)
            messages.append({"role": "user", "content": user_message})

            # Generate streaming response
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in streaming answer: {str(e)}")
            raise

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for RAG."""
        return """You are a helpful AI assistant that answers questions based on provided context from documents.

Your role:
1. Answer questions accurately using ONLY the information in the provided context
2. If the context doesn't contain enough information to answer, say so clearly
3. Cite sources by referencing document names and page numbers when possible
4. Be concise but thorough
5. If multiple documents discuss the topic, synthesize information from all relevant sources
6. Use clear formatting with bullet points or numbered lists when appropriate

Important guidelines:
- Don't make up information not present in the context
- Don't use external knowledge unless explicitly asked
- Always cite your sources using the format: [DocumentName.pdf, p.X]
- If uncertain, express your level of confidence
- Maintain a professional and helpful tone"""

    def _format_user_message(self, question: str, context: str) -> str:
        """
        Format the user message with question and context.

        Args:
            question: User's question
            context: Retrieved context

        Returns:
            Formatted message string
        """
        return f"""Context from documents:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. Remember to cite sources."""

    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Summarize a piece of text.

        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words

        Returns:
            Summary text
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a helpful assistant that creates concise summaries. Limit summaries to approximately {max_length} words."
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following text:\n\n{text}"
                }
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=max_length * 2  # Rough token estimate
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            raise

    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """
        Extract key terms from text.

        Args:
            text: Text to analyze
            num_keywords: Number of keywords to extract

        Returns:
            List of keywords
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"Extract the {num_keywords} most important keywords or phrases from the text. Return only the keywords, one per line."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=200
            )

            keywords = response.choices[0].message.content.strip().split('\n')
            return [kw.strip('- ').strip() for kw in keywords if kw.strip()]

        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            raise


# Singleton instance
llm_service = LLMService()
