"""
Tests for games toggles.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase

from games.toggles import is_games_xblock_enabled, ENABLE_GAMES_XBLOCK


class TestGamesXBlockToggles(TestCase):
    """Tests for games xblock toggle functions."""

    @patch.object(ENABLE_GAMES_XBLOCK, 'is_enabled')
    def test_is_games_xblock_enabled_when_flag_is_on(self, mock_is_enabled):
        """Test that function returns True when waffle flag is enabled."""
        mock_is_enabled.return_value = True
        self.assertTrue(is_games_xblock_enabled())
        mock_is_enabled.assert_called_once()

    @patch.object(ENABLE_GAMES_XBLOCK, 'is_enabled')
    def test_is_games_xblock_enabled_when_flag_is_off(self, mock_is_enabled):
        """Test that function returns False when waffle flag is disabled."""
        mock_is_enabled.return_value = False
        self.assertFalse(is_games_xblock_enabled())
        mock_is_enabled.assert_called_once()

    @patch.object(ENABLE_GAMES_XBLOCK, 'is_enabled')
    def test_is_games_xblock_enabled_handles_exception(self, mock_is_enabled):
        """Test that function returns False when exception occurs."""
        mock_is_enabled.side_effect = Exception("Database connection error")
        self.assertFalse(is_games_xblock_enabled())
        mock_is_enabled.assert_called_once()
