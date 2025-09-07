import re
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
from services.pinecone_service import pinecone_service

class CardSearchService:
    """
    Robust card search service that handles case sensitivity, typos, and variations.
    """
    
    def __init__(self):
        self.pinecone_service = pinecone_service
    
    def normalize_card_name(self, card_name: str) -> str:
        """
        Normalize card name for consistent searching.
        """
        # Remove extra whitespace and normalize case
        normalized = re.sub(r'\s+', ' ', card_name.strip())
        return normalized
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two card names (0.0 to 1.0).
        """
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
    
    def find_best_match(self, target_name: str, candidate_names: List[str], threshold: float = 0.8) -> Optional[str]:
        """
        Find the best matching card name from a list of candidates.
        """
        if not candidate_names:
            return None
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidate_names:
            score = self.calculate_similarity(target_name, candidate)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate
        
        return best_match
    
    def search_card_flexible(self, card_name: str, deck_name: str, max_results: int = 10) -> List[Dict]:
        """
        Search for a card with flexible matching (case-insensitive, fuzzy matching).
        """
        # First try exact match (case-insensitive)
        dummy_vector = [0.0] * 384
        
        # Try exact match first
        exact_filter = {"deck_name": deck_name, "card_name": card_name}
        results = self.pinecone_service.query(
            dense_vector=dummy_vector,
            top_k=1,
            filter=exact_filter
        )
        
        if results['matches']:
            return results['matches']
        
        # If no exact match, get all cards from the deck and do fuzzy matching
        deck_filter = {"deck_name": deck_name}
        all_cards = self.pinecone_service.query(
            dense_vector=dummy_vector,
            top_k=max_results,
            filter=deck_filter
        )
        
        if not all_cards['matches']:
            return []
        
        # Extract card names and find best match
        candidate_names = [match['metadata']['card_name'] for match in all_cards['matches']]
        best_match = self.find_best_match(card_name, candidate_names, threshold=0.7)
        
        if best_match:
            # Return the match with the best matching name
            for match in all_cards['matches']:
                if match['metadata']['card_name'] == best_match:
                    return [match]
        
        return []
    
    def search_combination_flexible(self, card_names: List[str], combination_deck: str) -> Optional[Dict]:
        """
        Search for a card combination with flexible matching.
        """
        dummy_vector = [0.0] * 384
        
        # Try different combination formats
        combination_formats = [
            ", ".join(card_names),  # "Card1, Card2, Card3"
            " and ".join(card_names),  # "Card1 and Card2 and Card3"
            " & ".join(card_names),  # "Card1 & Card2 & Card3"
        ]
        
        # For 2-card combinations, also try "Card1 and Card2" format
        if len(card_names) == 2:
            combination_formats.append(f"{card_names[0]} and {card_names[1]}")
        
        for combo_format in combination_formats:
            combo_filter = {"deck_name": combination_deck, "card_name": combo_format}
            results = self.pinecone_service.query(
                dense_vector=dummy_vector,
                top_k=1,
                filter=combo_filter
            )
            
            if results['matches']:
                return results['matches'][0]
        
        # If no exact match, try fuzzy matching on all combinations in the deck
        deck_filter = {"deck_name": combination_deck}
        all_combinations = self.pinecone_service.query(
            dense_vector=dummy_vector,
            top_k=20,
            filter=deck_filter
        )
        
        if not all_combinations['matches']:
            return None
        
        # Try to find a combination that contains all the requested cards
        target_cards_lower = [name.lower() for name in card_names]
        
        for match in all_combinations['matches']:
            combo_name = match['metadata']['card_name']
            combo_cards_lower = [card.strip().lower() for card in re.split(r'[,&]| and ', combo_name)]
            
            # Check if all target cards are present in this combination
            if all(any(self.calculate_similarity(target, combo_card) > 0.8 for combo_card in combo_cards_lower) 
                   for target in target_cards_lower):
                return match
        
        return None
    
    def find_cards_robust(self, card_names: List[str], deck_name: str) -> Tuple[List[Dict], bool]:
        """
        Robustly find cards, handling case sensitivity and typos.
        Returns (found_cards, found_all).
        """
        found_cards = []
        found_all = True
        
        for card_name in card_names:
            normalized_name = self.normalize_card_name(card_name)
            
            # Try flexible search
            matches = self.search_card_flexible(normalized_name, deck_name)
            
            if matches:
                found_cards.append(matches[0])
            else:
                found_all = False
                # Log the missing card for debugging
                print(f"Warning: Could not find card '{card_name}' in deck '{deck_name}'")
        
        return found_cards, found_all
    
    def find_combination_robust(self, card_names: List[str], num_cards: int) -> Optional[Dict]:
        """
        Robustly find card combinations.
        """
        combination_decks = {
            2: "two_card_combinations",
            3: "three_card_combinations", 
            5: "five_card_combinations"
        }
        
        if num_cards not in combination_decks:
            return None
        
        return self.search_combination_flexible(card_names, combination_decks[num_cards])

# Create global instance
card_search_service = CardSearchService()
