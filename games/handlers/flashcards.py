"""
Flashcards game handler methods.

This module contains handlers specific to the flashcards game type.
"""

import random


class FlashcardsHandlers:
    """Handlers specific to the flashcards game."""

    @staticmethod
    def start_game_flashcards(xblock, data, suffix=""):
        """A handler to begin the flashcards game."""
        cards = list(xblock.cards)

        if xblock.is_shuffled:
            random.shuffle(cards)

        return {
            "list": cards,
            "list_index": xblock.list_index,
            "list_length": xblock.list_length,
        }
