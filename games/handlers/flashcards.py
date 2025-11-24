"""
Flashcards game handler methods.

This module contains handlers specific to the flashcards game type.
"""

import random

import pkg_resources
from web_fragments.fragment import Fragment


class FlashcardsHandlers:
    """Handlers specific to the flashcards game."""

    @staticmethod
    def student_view(xblock, context=None):
        """
        The student view for flashcards game.
        """
        html = pkg_resources.resource_string(__name__, "../static/html/flashcards.html")
        frag = Fragment(html.decode("utf8"))
        frag.add_css(
            pkg_resources.resource_string(
                __name__, "../static/css/flashcards.css"
            ).decode("utf8")
        )
        return frag

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
