"""
Flashcards game handler methods.

This module contains handlers specific to the flashcards game type.
"""


class FlashcardsHandlers:
    """Handlers specific to the flashcards game."""

    @staticmethod
    def start_game_flashcards(xblock, data, suffix=""):
        """A handler to begin the flashcards game."""
        return {
            "list": xblock.list,
            "list_index": xblock.list_index,
            "list_length": xblock.list_length,
        }

    @staticmethod
    def flip_flashcard(xblock, data, suffix=""):
        """A handler to flip the flashcard from term to definition and vice versa."""
        if xblock.term_is_visible:
            xblock.term_is_visible = not (xblock.term_is_visible)
            return {
                "image": xblock.list[xblock.list_index]["definition_image"],
                "text": xblock.list[xblock.list_index]["definition"],
            }

        xblock.term_is_visible = not (xblock.term_is_visible)
        return {
            "image": xblock.list[xblock.list_index]["term_image"],
            "text": xblock.list[xblock.list_index]["term"],
        }

    @staticmethod
    def page_turn(xblock, data, suffix=""):
        """A handler to turn the page to a new flashcard (left or right) in the list."""
        # Always display the term first for a new flashcard.
        xblock.term_is_visible = True

        if data["nextIndex"] == "left":
            if xblock.list_index > 0:
                xblock.list_index -= 1
            # else if the current index is 0, circulate to the last flashcard
            else:
                xblock.list_index = len(xblock.list) - 1
            return {
                "term_image": xblock.list[xblock.list_index]["term_image"],
                "term": xblock.list[xblock.list_index]["term"],
                "index": xblock.list_index + 1,
                "list_length": xblock.list_length,
            }

        # else data['nextIndex'] == 'right'
        if xblock.list_index < len(xblock.list) - 1:
            xblock.list_index += 1
        # else if the current index is the last flashcard, circulate to the first flashcard
        else:
            xblock.list_index = 0
        return {
            "term_image": xblock.list[xblock.list_index]["term_image"],
            "term": xblock.list[xblock.list_index]["term"],
            "index": xblock.list_index + 1,
            "list_length": xblock.list_length,
        }
