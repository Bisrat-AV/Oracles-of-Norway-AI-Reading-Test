import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.process_data import parse_oracle_cards_by_deck, parse_two_card_readings
from db.models import Deck, Card, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestDataProcessing(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = TestSessionLocal()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_parse_oracle_cards_by_deck(self):
        # Create a dummy file
        with open("test_oracle_cards.md", "w") as f:
            f.write("# Deck: Test Deck 1\n")
            f.write("## Card 1\n")
            f.write("Interpretation 1\n")
        
        decks = parse_oracle_cards_by_deck("test_oracle_cards.md")
        self.assertIn("Test Deck 1", decks)
        self.assertEqual(len(decks["Test Deck 1"]), 1)
        self.assertEqual(decks["Test Deck 1"][0]['name'], "Card 1")
        self.assertIn("Interpretation 1", decks["Test Deck 1"][0]['interpretation'])
        
        os.remove("test_oracle_cards.md")

    def test_parse_two_card_readings(self):
        # Create a dummy file
        with open("test_two_card_readings.md", "w") as f:
            f.write("# Deck: SENSITIVE SOUL\n\n")
            f.write("## Radiant Light\n")
            f.write("Interpretation for Radiant Light.\n")
            f.write("---\n")
            f.write("## Toxic Energy\n")
            f.write("Interpretation for Toxic Energy.\n")

        decks = parse_two_card_readings("test_two_card_readings.md")
        self.assertIn("SENSITIVE SOUL", decks)
        self.assertEqual(len(decks["SENSITIVE SOUL"]), 2)
        self.assertEqual(decks["SENSITIVE SOUL"][0]['name'], "Radiant Light")
        self.assertIn("Interpretation for Radiant Light", decks["SENSITIVE SOUL"][0]['interpretation'])

        os.remove("test_two_card_readings.md")

if __name__ == '__main__':
    unittest.main()
