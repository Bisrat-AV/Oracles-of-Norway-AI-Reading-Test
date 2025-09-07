import os
from openai import OpenAI
from dotenv import load_dotenv
from .prompt_service import prompt_service

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_reading(self, card_names: list, context: str, theme: str = "default", user_query: str = None) -> str:
        """
        Generates an oracle reading using the provided context, theme, and optional user query.
        
        Args:
            card_names: List of card names
            context: Card context from database
            theme: Theme for the reading (default, love, career, etc.)
            user_query: Optional user question/query
        """
        # Get system message and construct prompt using the prompt service
        system_message = prompt_service.get_system_message(theme)
        prompt = prompt_service.construct_prompt(
            card_names=card_names,
            context=context,
            theme=theme,
            user_query=user_query
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content



llm_service = LLMService()
