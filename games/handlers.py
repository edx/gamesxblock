"""
Handler methods for the Games XBlock.

This module contains all the handler methods that respond to AJAX requests
from the frontend, separated from the main XBlock class for better organization.
"""
import hashlib
import random
import string

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from xblock.core import Response

from .constants import (
    CARD_FIELD,
    CONFIG,
    CONTAINER_TYPE,
    DEFAULT,
    GAME_TYPE,
    UPLOAD,
)


class UniversalHandlers:
    """Handlers that work across all game types."""

    @staticmethod
    def expand_game(xblock, data, suffix=''):
        """A handler to expand the game from its title block."""
        description = "ERR: self.game_type not defined or invalid"
        if xblock.game_type == GAME_TYPE.FLASHCARDS:
            description = "Click each card to reveal the definition"
        elif xblock.game_type == GAME_TYPE.MATCHING:
            description = "Match each term with the correct definition"
        return {
            'title': xblock.title,
            'description': description,
            'game_type': xblock.game_type
        }

    @staticmethod
    def get_settings(xblock, data, suffix=""):
        """Get game type, cards, and shuffle setting in one call."""
        return {
            "game_type": xblock.game_type,
            "cards": xblock.cards,
            "is_shuffled": xblock.is_shuffled,
        }

    @staticmethod
    def upload_image(xblock, request, suffix=""):
        """Upload an image file and return the URL."""
        try:
            upload_file = request.params["file"].file
            file_name = request.params["file"].filename
            file_hash = hashlib.md5(upload_file.read()).hexdigest()
            upload_file.seek(0)
            _, ext = (
                file_name.rsplit(".", 1) if "." in file_name else (file_name, UPLOAD.DEFAULT_EXTENSION)
            )
            file_path = f"{UPLOAD.PATH_PREFIX}/{xblock.scope_ids.usage_id.block_id}/{file_hash}.{ext}"
            saved_path = default_storage.save(
                file_path, ContentFile(upload_file.read())
            )
            file_url = default_storage.url(saved_path)
            return Response(
                json_body={"success": True, "url": file_url, "filename": file_name}
            )
        except Exception as e:
            return Response(json_body={"success": False, "error": str(e)}, status=400)

    @staticmethod
    def save_settings(xblock, data, suffix=""):
        """
        Save game type, shuffle setting, and all cards in one API call.
        Expected data format:
        {
            'game_type': 'flashcards' or 'matching',
            'is_shuffled': true or false,
            'cards': [
                {
                    'term': 'Term 1',
                    'term_image': 'http://...',
                    'definition': 'Definition 1',
                    'definition_image': 'http://...'
                },
                ...
            ]
        }
        """
        try:
            new_game_type = data.get("game_type", GAME_TYPE.FLASHCARDS)
            new_is_shuffled = data.get("is_shuffled", DEFAULT.IS_SHUFFLED)
            new_cards = data.get("cards", [])

            validated_cards = []
            for card in new_cards:
                if not isinstance(card, dict):
                    return {"success": False, "error": "Each card must be an object"}

                # Validate required fields
                if CARD_FIELD.TERM not in card or CARD_FIELD.DEFINITION not in card:
                    return {
                        "success": False,
                        "error": "Each card must have term and definition",
                    }

                validated_cards.append(
                    {
                        CARD_FIELD.TERM: card.get(CARD_FIELD.TERM, ""),
                        CARD_FIELD.TERM_IMAGE: card.get(CARD_FIELD.TERM_IMAGE, ""),
                        CARD_FIELD.DEFINITION: card.get(CARD_FIELD.DEFINITION, ""),
                        CARD_FIELD.DEFINITION_IMAGE: card.get(CARD_FIELD.DEFINITION_IMAGE, ""),
                        CARD_FIELD.ORDER: card.get(CARD_FIELD.ORDER, ""),
                    }
                )

            xblock.cards = validated_cards
            xblock.game_type = new_game_type
            xblock.is_shuffled = new_is_shuffled

            xblock.save()

            return {
                "success": True,
                "game_type": xblock.game_type,
                "cards": xblock.cards,
                "count": len(xblock.cards),
                "is_shuffled": xblock.is_shuffled,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def close_game(xblock, data, suffix=''):
        """A handler to close the game to its title block."""
        xblock.game_started = False
        xblock.time_seconds = 0
        xblock.match_count = 0
        xblock.matches_remaining = xblock.list_length

        if xblock.game_type == GAME_TYPE.FLASHCARDS:
            xblock.term_is_visible = True
            xblock.list_index = 0
        return {
            'title': xblock.title
        }

    @staticmethod
    def display_help(xblock, data, suffix=''):
        """A handler to display a tooltip message above the help icon."""
        message = "ERR: self.game_type not defined or invalid"
        if xblock.game_type == GAME_TYPE.FLASHCARDS:
            message = "Click each card to reveal the definition"
        elif xblock.game_type == GAME_TYPE.MATCHING:
            message = "Match each term with the correct definition"
        return {'message': message}


class FlashcardsHandlers:
    """Handlers specific to the flashcards game."""

    @staticmethod
    def start_game_flashcards(xblock, data, suffix=''):
        """A handler to begin the flashcards game."""
        return {
            'list': xblock.list,
            'list_index': xblock.list_index,
            'list_length': xblock.list_length
        }

    @staticmethod
    def flip_flashcard(xblock, data, suffix=''):
        """A handler to flip the flashcard from term to definition and vice versa."""
        if xblock.term_is_visible:
            xblock.term_is_visible = not(xblock.term_is_visible)
            return {
                'image': xblock.list[xblock.list_index]['definition_image'],
                'text': xblock.list[xblock.list_index]['definition']
            }

        xblock.term_is_visible = not(xblock.term_is_visible)
        return {
            'image': xblock.list[xblock.list_index]['term_image'],
            'text': xblock.list[xblock.list_index]['term']
        }

    @staticmethod
    def page_turn(xblock, data, suffix=''):
        """A handler to turn the page to a new flashcard (left or right) in the list."""
        # Always display the term first for a new flashcard.
        xblock.term_is_visible = True

        if data['nextIndex'] == 'left':
            if xblock.list_index > 0:
                xblock.list_index -= 1
            # else if the current index is 0, circulate to the last flashcard
            else:
                xblock.list_index = len(xblock.list) - 1
            return {
                'term_image': xblock.list[xblock.list_index]['term_image'],
                'term': xblock.list[xblock.list_index]['term'],
                'index': xblock.list_index + 1,
                'list_length': xblock.list_length
            }

        # else data['nextIndex'] == 'right'
        if xblock.list_index < len(xblock.list) - 1:
            xblock.list_index += 1
        # else if the current index is the last flashcard, circulate to the first flashcard
        else:
            xblock.list_index = 0
        return {
            'term_image': xblock.list[xblock.list_index]['term_image'],
            'term': xblock.list[xblock.list_index]['term'],
            'index': xblock.list_index + 1,
            'list_length': xblock.list_length
        }


class MatchingHandlers:
    """Handlers specific to the matching game."""

    @staticmethod
    def _random_string():
        """Generate a random ASCII string of configured length (upper- and lower-case)."""
        return str(''.join(random.choices(string.ascii_letters, k=CONFIG.RANDOM_STRING_LENGTH)))

    @staticmethod
    def start_game_matching(xblock, data, suffix=''):
        """A handler to begin the matching game."""
        # Set game fields accordingly
        xblock.game_started = True
        xblock.time_seconds = 0
        xblock.selected_containers = {}
        xblock.match_count = 0
        xblock.matches_remaining = xblock.list_length

        # Create dictionaries and key-value pairs to reference the list based on ids
        for i in range(0, 2 * xblock.list_length, 2):
            # The ids are random strings stored into an indexed list
            unique_string = MatchingHandlers._random_string()
            while unique_string in xblock.matching_id_list:
                unique_string = MatchingHandlers._random_string()
            xblock.matching_id_list.append(unique_string)  # append id at index i

            while unique_string in xblock.matching_id_list:
                unique_string = MatchingHandlers._random_string()
            xblock.matching_id_list.append(unique_string)  # append id at index i+1

            # The random string ids are the dictionary keys for the indices, types, and content
            xblock.matching_id_dictionary_index[xblock.matching_id_list[i]] = i // 2
            xblock.matching_id_dictionary_index[xblock.matching_id_list[i + 1]] = i // 2

            xblock.matching_id_dictionary_type[xblock.matching_id_list[i]] = CONTAINER_TYPE.TERM
            xblock.matching_id_dictionary_type[xblock.matching_id_list[i + 1]] = CONTAINER_TYPE.DEFINITION

            xblock.matching_id_dictionary[xblock.matching_id_list[i]] = xblock.list[i // 2]['term']
            xblock.matching_id_dictionary[xblock.matching_id_list[i + 1]] = xblock.list[i // 2]['definition']

        return {
            'list': xblock.list,
            'list_index': xblock.list_index,
            'list_length': xblock.list_length,
            'id_dictionary_index': xblock.matching_id_dictionary_index,
            'id_dictionary': xblock.matching_id_dictionary,
            'id_list': xblock.matching_id_list,
            'time': "0:00"
        }

    @staticmethod
    def update_timer(xblock, data, suffix=''):
        """Update the timer. This is called every 1000ms by an ajax call."""
        # Only increment the timer if the game has started
        if xblock.game_started:
            xblock.time_seconds += 1

        return {'value': xblock.time_seconds, 'game_started': xblock.game_started}

    @staticmethod
    def select_container(xblock, data, suffix=''):
        """Handler for selecting matching game containers and evaluating matches."""
        # Add a '#' to id for use with jQuery
        id = "#" + data['id']
        container_type = xblock.matching_id_dictionary_type[data['id']]
        index = xblock.matching_id_dictionary_index[data['id']]

        # If no container is selected yet
        if len(xblock.selected_containers) == 0:
            xblock.selected_containers['container1_id'] = id
            xblock.selected_containers['container1_type'] = container_type
            xblock.selected_containers['container1_index'] = index
            return {
                'first_selection': True, 'deselect': False, 'id': id, 'prev_id': None,
                'match': False, 'match_count': xblock.match_count,
                'matches_remaining': xblock.matches_remaining, 'list': xblock.list,
                'list_length': xblock.list_length, 'id_list': xblock.matching_id_list,
                'id_dictionary': xblock.matching_id_dictionary, 'time_seconds': xblock.time_seconds
            }

        # Establish prev_id before conditionals
        prev_id = xblock.selected_containers['container1_id']

        # If the container referenced by 'id' is already selected, deselect it
        if id == xblock.selected_containers['container1_id']:
            xblock.selected_containers.clear()
            return {
                'first_selection': False, 'deselect': True, 'id': id, 'prev_id': prev_id,
                'match': False, 'match_count': xblock.match_count,
                'matches_remaining': xblock.matches_remaining, 'list': xblock.list,
                'list_length': xblock.list_length, 'id_list': xblock.matching_id_list,
                'id_dictionary': xblock.matching_id_dictionary, 'time_seconds': xblock.time_seconds
            }

        # Containers with the same type cannot match (i.e. a term with a term, etc.)
        if container_type == xblock.selected_containers['container1_type']:
            xblock.selected_containers.clear()
            return {
                'first_selection': False, 'deselect': False, 'id': id, 'prev_id': prev_id,
                'match': False, 'match_count': xblock.match_count,
                'matches_remaining': xblock.matches_remaining, 'list': xblock.list,
                'list_length': xblock.list_length, 'id_list': xblock.matching_id_list,
                'id_dictionary': xblock.matching_id_dictionary, 'time_seconds': xblock.time_seconds
            }

        # If the execution gets to this point and the indices are the same, this is a match
        if index == xblock.selected_containers['container1_index']:
            xblock.selected_containers.clear()
            xblock.match_count += 1
            xblock.matches_remaining -= 1
            return {
                'first_selection': False, 'deselect': False, 'id': id, 'prev_id': prev_id,
                'match': True, 'match_count': xblock.match_count,
                'matches_remaining': xblock.matches_remaining, 'list': xblock.list,
                'list_length': xblock.list_length, 'id_list': xblock.matching_id_list,
                'id_dictionary': xblock.matching_id_dictionary, 'time_seconds': xblock.time_seconds
            }

        # Not a match
        xblock.selected_containers.clear()
        return {
            'first_selection': False, 'deselect': False, 'id': id, 'prev_id': prev_id,
            'match': False, 'match_count': xblock.match_count,
            'matches_remaining': xblock.matches_remaining, 'list': xblock.list,
            'list_length': xblock.list_length, 'id_list': xblock.matching_id_list,
            'id_dictionary': xblock.matching_id_dictionary, 'time_seconds': xblock.time_seconds
        }

    @staticmethod
    def end_game_matching(xblock, data, suffix=''):
        """End the matching game and compare the user's time to the best_time field."""
        xblock.game_started = False
        xblock.time_seconds = 0
        xblock.selected_containers = {}
        xblock.match_count = 0
        xblock.matches_remaining = xblock.list_length

        new_time = data['newTime']
        prev_time = xblock.best_time
        new_record = False
        first_attempt = False

        # Update record if it is beaten
        if xblock.best_time is None:
            first_attempt = True
            new_record = True
            xblock.best_time = new_time
            return {
                'new_time': new_time, 'prev_time': prev_time,
                'new_record': new_record, 'first_attempt': first_attempt
            }

        if new_time < xblock.best_time:
            new_record = True
            xblock.best_time = new_time

        return {
            'new_time': new_time, 'prev_time': prev_time,
            'new_record': new_record, 'first_attempt': first_attempt
        }
