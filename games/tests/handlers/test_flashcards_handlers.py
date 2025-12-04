"""
Tests for flashcards and matching handlers.
"""
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from faker import Faker
from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds

from games.games import GamesXBlock
from games.handlers.flashcards import FlashcardsHandlers
from games.constants import GAME_TYPE, CARD_FIELD


class TestFlashcardsHandlers(TestCase):
    """Tests for flashcards handler methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.fake = Faker()
        self.runtime = Mock()
        self.scope_ids = ScopeIds(self.fake.uuid4(), "games", self.fake.uuid4(), self.fake.uuid4())
        self.title = self.fake.catch_phrase()
        self.field_data = DictFieldData({
            'game_type': GAME_TYPE.FLASHCARDS,
            'cards': [
                {CARD_FIELD.CARD_KEY: self.fake.uuid4(), CARD_FIELD.TERM: self.fake.word(), CARD_FIELD.DEFINITION: self.fake.sentence()},
                {CARD_FIELD.CARD_KEY: self.fake.uuid4(), CARD_FIELD.TERM: self.fake.word(), CARD_FIELD.DEFINITION: self.fake.sentence()},
            ],
            'is_shuffled': self.fake.boolean(),
            'has_timer': self.fake.boolean(),
            'title': self.title,
        })
        self.xblock = GamesXBlock(self.runtime, self.field_data, self.scope_ids)

    @patch('games.handlers.flashcards.pkg_resources.resource_string')
    def test_student_view_renders_fragment(self, mock_resource_string):
        """Test student view returns a fragment with cards."""
        mock_resource_string.return_value = b'<div>{{ title }}</div>'

        frag = FlashcardsHandlers.student_view(self.xblock)

        self.assertIsNotNone(frag)
        self.assertIn(self.title, frag.content)

    @patch('games.handlers.flashcards.pkg_resources.resource_string')
    def test_student_view_with_shuffled_cards(self, mock_resource_string):
        """Test student view with shuffled cards."""
        mock_resource_string.return_value = b'<div>{{ list_length }}</div>'
        self.xblock.is_shuffled = True

        frag = FlashcardsHandlers.student_view(self.xblock)

        self.assertIsNotNone(frag)
        self.assertIn('2', frag.content)

    @patch('games.handlers.flashcards.pkg_resources.resource_string')
    def test_student_view_with_no_cards(self, mock_resource_string):
        """Test student view with no cards."""
        mock_resource_string.return_value = b'<div>{{ list_length }}</div>'
        self.xblock.cards = []

        frag = FlashcardsHandlers.student_view(self.xblock)

        self.assertIsNotNone(frag)
        self.assertIn('0', frag.content)