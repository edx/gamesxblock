"""
Matching game handler methods.

This module contains handlers specific to the matching game type.
"""

import base64
import json
import random
import string

import pkg_resources
from django.template import Context, Template
from web_fragments.fragment import Fragment

from ..constants import CONFIG, CONTAINER_TYPE


class MatchingHandlers:
    """Handlers specific to the matching game."""

    @staticmethod
    def student_view(xblock, context=None):
        """
        The student view for matching game.
        Uses django template for rendering dynamic content.
        """

        # Prepare data
        cards = list(xblock.cards) if xblock.cards else []
        if xblock.is_shuffled and cards:
            random.shuffle(cards)

        # Build mixed column data if shuffled, else original layout
        list_length = len(cards)
        if xblock.is_shuffled and cards:
            # Create items for both term and definition
            all_items = []
            for idx, card in enumerate(cards):
                all_items.append(
                    {
                        "idx": idx,
                        "kind": "term",
                        "id": f"term-{idx}",
                        "text": card.get("term", ""),
                    }
                )
                all_items.append(
                    {
                        "idx": idx,
                        "kind": "definition",
                        "id": f"def-{idx}",
                        "text": card.get("definition", ""),
                    }
                )
            random.shuffle(all_items)

            left_items = []
            right_items = []
            for item in all_items:
                # Ensure each column gets exactly list_length items
                if len(left_items) < list_length and len(right_items) < list_length:
                    if random.choice([True, False]):
                        left_items.append(item)
                    else:
                        right_items.append(item)
                elif len(left_items) < list_length:
                    left_items.append(item)
                else:
                    right_items.append(item)
        else:
            # Original separated layout (terms left, definitions right)
            left_items = []
            right_items = []
            for idx, card in enumerate(cards):
                left_items.append(
                    {
                        "idx": idx,
                        "kind": "term",
                        "id": f"term-{idx}",
                        "text": card.get("term", ""),
                    }
                )
                right_items.append(
                    {
                        "idx": idx,
                        "kind": "definition",
                        "id": f"def-{idx}",
                        "text": card.get("definition", ""),
                    }
                )

        template_context = {
            "title": xblock.title,
            "list_length": list_length,
            "left_items": left_items,
            "right_items": right_items,
        }

        # Obfuscated mapping: pairs with salt, base64 encoded
        salt = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        pairs = []
        for card in cards:
            pairs.append({"t": card.get("term", ""), "d": card.get("definition", "")})
        mapping_payload = {"pairs": pairs, "salt": salt}
        encoded_mapping = base64.b64encode(
            json.dumps(mapping_payload).encode()
        ).decode()

        # Generate random variable names for obfuscation
        var_names = {
            "runtime": "".join(
                random.choices(string.ascii_lowercase, k=random.randint(1, 3))
            ),
            "elem": "".join(
                random.choices(string.ascii_lowercase, k=random.randint(1, 3))
            ),
            "tag": "".join(
                random.choices(string.ascii_lowercase, k=random.randint(1, 3))
            ),
            "payload": "".join(
                random.choices(string.ascii_lowercase, k=random.randint(1, 3))
            ),
            "err": "".join(
                random.choices(string.ascii_lowercase, k=random.randint(1, 3))
            ),
        }
        # Build dynamically obfuscated decoder as named function
        # Generate random UUID for the data element
        data_element_id = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=16)
        )

        # Build dynamically obfuscated decoder as named function
        obf_decoder = (
            f"function MatchingInit({var_names['runtime']},{var_names['elem']}){{"
            f"var {var_names['tag']}=$('#{data_element_id}',{var_names['elem']});"
            f"if(!{var_names['tag']}.length)return;try{{"
            f"var {var_names['payload']}=JSON.parse(atob({var_names['tag']}.text()));"
            f"{var_names['tag']}.remove();if({var_names['payload']}&&{var_names['payload']}.pairs)"
            f"GamesXBlockMatchingInit({var_names['runtime']},{var_names['elem']},{var_names['payload']}.pairs);"
            f"}}catch({var_names['err']}){{console.warn('Decode failed');}}}}"
        )

        template_context["encoded_mapping"] = encoded_mapping
        template_context["obf_decoder"] = obf_decoder
        template_context["data_element_id"] = data_element_id

        # Render template
        template_str = pkg_resources.resource_string(
            __name__, "../static/html/matching.html"
        ).decode("utf8")
        template = Template(template_str)
        html = template.render(Context(template_context))

        frag = Fragment(html)
        # Attach matching-specific CSS and JS
        frag.add_css(
            pkg_resources.resource_string(
                __name__, "../static/css/matching.css"
            ).decode("utf8")
        )
        frag.add_javascript(
            pkg_resources.resource_string(
                __name__, "../static/js/src/matching.js"
            ).decode("utf8")
        )
        frag.initialize_js("MatchingInit")
        return frag

    @staticmethod
    def _random_string():
        """Generate a random ASCII string of configured length (upper- and lower-case)."""
        return str(
            "".join(random.choices(string.ascii_letters, k=CONFIG.RANDOM_STRING_LENGTH))
        )

    @staticmethod
    def start_game_matching(xblock, data, suffix=""):
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

            xblock.matching_id_dictionary_type[xblock.matching_id_list[i]] = (
                CONTAINER_TYPE.TERM
            )
            xblock.matching_id_dictionary_type[xblock.matching_id_list[i + 1]] = (
                CONTAINER_TYPE.DEFINITION
            )

            xblock.matching_id_dictionary[xblock.matching_id_list[i]] = xblock.list[
                i // 2
            ]["term"]
            xblock.matching_id_dictionary[xblock.matching_id_list[i + 1]] = xblock.list[
                i // 2
            ]["definition"]

        return {
            "list": xblock.cards,
            "list_index": xblock.list_index,
            "list_length": xblock.list_length,
            "id_dictionary_index": xblock.matching_id_dictionary_index,
            "id_dictionary": xblock.matching_id_dictionary,
            "id_list": xblock.matching_id_list,
            "time": "0:00",
        }

    @staticmethod
    def update_timer(xblock, data, suffix=""):
        """Update the timer. This is called every 1000ms by an ajax call."""
        # Only increment the timer if the game has started
        if xblock.game_started:
            xblock.time_seconds += 1

        return {"value": xblock.time_seconds, "game_started": xblock.game_started}

    @staticmethod
    def select_container(xblock, data, suffix=""):
        """Handler for selecting matching game containers and evaluating matches."""
        # Add a '#' to id for use with jQuery
        id = "#" + data["id"]
        container_type = xblock.matching_id_dictionary_type[data["id"]]
        index = xblock.matching_id_dictionary_index[data["id"]]

        # If no container is selected yet
        if len(xblock.selected_containers) == 0:
            xblock.selected_containers["container1_id"] = id
            xblock.selected_containers["container1_type"] = container_type
            xblock.selected_containers["container1_index"] = index
            return {
                "first_selection": True,
                "deselect": False,
                "id": id,
                "prev_id": None,
                "match": False,
                "match_count": xblock.match_count,
                "matches_remaining": xblock.matches_remaining,
                "list": xblock.cards,
                "list_length": xblock.list_length,
                "id_list": xblock.matching_id_list,
                "id_dictionary": xblock.matching_id_dictionary,
                "time_seconds": xblock.time_seconds,
            }

        # Establish prev_id before conditionals
        prev_id = xblock.selected_containers["container1_id"]

        # If the container referenced by 'id' is already selected, deselect it
        if id == xblock.selected_containers["container1_id"]:
            xblock.selected_containers.clear()
            return {
                "first_selection": False,
                "deselect": True,
                "id": id,
                "prev_id": prev_id,
                "match": False,
                "match_count": xblock.match_count,
                "matches_remaining": xblock.matches_remaining,
                "list": xblock.cards,
                "list_length": xblock.list_length,
                "id_list": xblock.matching_id_list,
                "id_dictionary": xblock.matching_id_dictionary,
                "time_seconds": xblock.time_seconds,
            }

        # Containers with the same type cannot match (i.e. a term with a term, etc.)
        if container_type == xblock.selected_containers["container1_type"]:
            xblock.selected_containers.clear()
            return {
                "first_selection": False,
                "deselect": False,
                "id": id,
                "prev_id": prev_id,
                "match": False,
                "match_count": xblock.match_count,
                "matches_remaining": xblock.matches_remaining,
                "list": xblock.cards,
                "list_length": xblock.list_length,
                "id_list": xblock.matching_id_list,
                "id_dictionary": xblock.matching_id_dictionary,
                "time_seconds": xblock.time_seconds,
            }

        # If the execution gets to this point and the indices are the same, this is a match
        if index == xblock.selected_containers["container1_index"]:
            xblock.selected_containers.clear()
            xblock.match_count += 1
            xblock.matches_remaining -= 1
            return {
                "first_selection": False,
                "deselect": False,
                "id": id,
                "prev_id": prev_id,
                "match": True,
                "match_count": xblock.match_count,
                "matches_remaining": xblock.matches_remaining,
                "list": xblock.cards,
                "list_length": xblock.list_length,
                "id_list": xblock.matching_id_list,
                "id_dictionary": xblock.matching_id_dictionary,
                "time_seconds": xblock.time_seconds,
            }

        # Not a match
        xblock.selected_containers.clear()
        return {
            "first_selection": False,
            "deselect": False,
            "id": id,
            "prev_id": prev_id,
            "match": False,
            "match_count": xblock.match_count,
            "matches_remaining": xblock.matches_remaining,
            "list": xblock.cards,
            "list_length": xblock.list_length,
            "id_list": xblock.matching_id_list,
            "id_dictionary": xblock.matching_id_dictionary,
            "time_seconds": xblock.time_seconds,
        }

    @staticmethod
    def end_game_matching(xblock, data, suffix=""):
        """End the matching game and compare the user's time to the best_time field."""
        xblock.game_started = False
        xblock.time_seconds = 0
        xblock.selected_containers = {}
        xblock.match_count = 0
        xblock.matches_remaining = xblock.list_length

        new_time = data["newTime"]
        prev_time = xblock.best_time
        new_record = False
        first_attempt = False

        # Update record if it is beaten
        if xblock.best_time is None:
            first_attempt = True
            new_record = True
            xblock.best_time = new_time
            return {
                "new_time": new_time,
                "prev_time": prev_time,
                "new_record": new_record,
                "first_attempt": first_attempt,
            }

        if new_time < xblock.best_time:
            new_record = True
            xblock.best_time = new_time

        return {
            "new_time": new_time,
            "prev_time": prev_time,
            "new_record": new_record,
            "first_attempt": first_attempt,
        }
