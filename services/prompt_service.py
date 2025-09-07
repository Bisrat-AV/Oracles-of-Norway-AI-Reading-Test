import os
import yaml
from typing import Dict, Optional, Any
from pathlib import Path

class PromptService:
    """
    Service for loading and managing oracle card reading prompts.
    Handles theme-specific prompts and user query integration.
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._base_prompt = None
        self._theme_prompts = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load all prompt files from the prompts directory"""
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory not found: {self.prompts_dir}")
        
        # Load base prompt
        base_file = self.prompts_dir / "base_prompt.yaml"
        if base_file.exists():
            with open(base_file, 'r', encoding='utf-8') as f:
                self._base_prompt = yaml.safe_load(f)
        else:
            raise FileNotFoundError("Base prompt file not found: base_prompt.yaml")
        
        # Load theme prompts
        for theme_file in self.prompts_dir.glob("theme_*.yaml"):
            theme_name = theme_file.stem.replace("theme_", "")
            with open(theme_file, 'r', encoding='utf-8') as f:
                self._theme_prompts[theme_name] = yaml.safe_load(f)
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get list of available themes with their descriptions"""
        return {
            theme_name: theme_data.get("description", "No description available")
            for theme_name, theme_data in self._theme_prompts.items()
        }
    
    def get_system_message(self, theme: str = "default") -> str:
        """Get the system message for the specified theme"""
        if not self._base_prompt:
            raise ValueError("Base prompt not loaded")
        
        return self._base_prompt["system_message"]
    
    def construct_prompt(
        self, 
        card_names: list, 
        context: str, 
        theme: str = "default",
        user_query: Optional[str] = None
    ) -> str:
        """
        Construct a complete prompt for the LLM based on theme and user input.
        
        Args:
            card_names: List of card names
            context: Card context from database
            theme: Theme name (default, love, career, etc.)
            user_query: Optional user question/query
            
        Returns:
            Complete formatted prompt string
        """
        if not self._base_prompt:
            raise ValueError("Base prompt not loaded")
        
        # Get theme-specific data
        theme_data = self._theme_prompts.get(theme, self._theme_prompts.get("default", {}))
        
        # Format card names
        card_list = ", ".join(f"'{name}'" for name in card_names)
        
        # Check if we need synthesis example
        needs_synthesis_example = "Combined Interpretation" not in context
        synthesis_example = ""
        if needs_synthesis_example:
            synthesis_example = self._base_prompt["synthesis_example"]
        
        # Handle user query
        user_query_section = ""
        if user_query and user_query.strip():
            user_query_prompt = theme_data.get("user_query_prompt", "").format(user_query=user_query)
            # If no user_query_section is defined, use the user_query_prompt directly
            if theme_data.get("user_query_section"):
                user_query_section = theme_data.get("user_query_section", "").format(
                    user_query_prompt=user_query_prompt
                )
            else:
                user_query_section = user_query_prompt
        
        # Get theme guidance
        theme_guidance = theme_data.get("theme_guidance", "")
        
        # Construct the complete prompt
        prompt_parts = []
        
        if synthesis_example:
            prompt_parts.append(synthesis_example)
        
        prompt_parts.append("### CONTEXT FOR YOUR READING")
        prompt_parts.append("---")
        prompt_parts.append(context)
        prompt_parts.append("---")
        
        if theme_guidance:
            prompt_parts.append("### THEME GUIDANCE")
            prompt_parts.append(theme_guidance)
            prompt_parts.append("---")
        
        if user_query_section:
            prompt_parts.append("### USER QUERY")
            prompt_parts.append(user_query_section)
            prompt_parts.append("---")
        
        # Add base instructions
        base_instructions = self._base_prompt["base_instructions"].format(card_names=card_list)
        prompt_parts.append("### INSTRUCTIONS")
        prompt_parts.append(base_instructions)
        
        # Add final reading request
        prompt_parts.append("### YOUR READING REQUEST")
        prompt_parts.append(f"Provide a reading for the cards: {card_list}.")
        
        return "\n\n".join(prompt_parts)
    
    def reload_prompts(self):
        """Reload all prompts from files (useful for development)"""
        self._base_prompt = None
        self._theme_prompts = {}
        self._load_prompts()

# Global instance
prompt_service = PromptService()
