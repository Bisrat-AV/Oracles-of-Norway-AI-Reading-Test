import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_reading(self, card_names: list, context: str) -> str:
        """
        Generates an oracle reading using the provided context.
        """
        prompt = self._construct_prompt(card_names, context)
        
        system_message = "You are the Oracle of Norway, a wise and insightful spiritual guide. Your readings are poetic, deep, and provide a cohesive narrative that weaves together the meanings of the selected cards. You must ONLY use the provided context to formulate your reading."

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    def _construct_prompt(self, card_names: list, context: str) -> str:
        """
        Constructs the prompt for the LLM. If no pre-written combination is in the
        context, it includes a few-shot example to guide the model's synthesis.
        """
        card_list = ", ".join(f"'{name}'" for name in card_names)
        
        # Check if we are dealing with individual cards that need synthesis
        needs_synthesis_example = "Combined Interpretation" not in context

        few_shot_example = ""
        if needs_synthesis_example:
            few_shot_example = """
            ### EXAMPLE OF A SYNTHESIZED READING
            ---
            Here is an example of how to synthesize a reading from individual card meanings.

            CONTEXT:
            Card Name: Roots
            Interpretation: This card signifies cutting away old patterns. It is a powerful card of new beginnings, signaling a completely different life is on its way because the old karmic cycle has ended.
            ---
            Card Name: Blister
            Interpretation: This card represents repeating the mistakes of the past, like wearing the same old shoes even though you know they give you blisters. It is an urge to learn from life's lessons.
            ---

            SYNTHESIZED READING:
            The appearance of 'Roots' and 'Blister' together brings a profound message about the cycles of your life. There is a powerful opportunity for a new beginning, as 'Roots' suggests you have successfully cut away the old karmic patterns that no longer serve you. However, the 'Blister' serves as a crucial reminder to remain vigilant. It warns against the temptation to step back into old, painful situations—the 'old shoes'—out of habit or comfort. Your task now is to consciously embrace the new path that is opening up for you, trusting that the lessons of the past have been learned and that you deserve to walk forward without the familiar pain of old blisters.
            ---
            """

        return f"""
        {few_shot_example}
        ### CONTEXT FOR YOUR READING
        ---
        {context}
        ---

        ### INSTRUCTIONS
        Based ONLY on the 'CONTEXT FOR YOUR READING' provided above, provide a synthesized oracle reading for a user who drew the cards {card_list}.
        1. Start with a brief, overarching summary of the combined energy of the cards.
        2. Explain how the individual energies of the cards contribute to this central theme.
        3. Conclude with guidance or a final thought for the user.
        4. Maintain a mystical, supportive, and insightful tone throughout. Do not simply list the interpretations; weave them into a single, flowing narrative like in the example.

        ### YOUR READING REQUEST
        Provide a reading for the cards: {card_list}.
        """

llm_service = LLMService()
