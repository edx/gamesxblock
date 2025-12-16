"""
Matching game handler methods.

This module contains handlers specific to the matching game type.
"""

import base64
import json
import random
import string

import pkg_resources
from xblock.core import Response
from django.template import Context, Template
from web_fragments.fragment import Fragment
from ..constants import CONFIG, DEFAULT
from .common import CommonHandlers


class MatchingHandlers:
    """Handlers specific to the matching game type."""

    @staticmethod
    def student_view(xblock, context=None):
        """Render the student view for the matching game."""
        # Prepare cards
        cards = list(xblock.cards) if xblock.cards else []
        list_length = len(cards)

        # Split cards into pages based on MATCHES_PER_PAGE
        matches_per_page = CONFIG.MATCHES_PER_PAGE
        pages = []
        for i in range(0, len(cards), matches_per_page):
            page_cards = cards[i:i + matches_per_page]
            pages.append(page_cards)

        # Pre-generate all random keys in one batch (hex digits for maximum confusion)
        total_items = len(cards) * 2
        key_length = CONFIG.RANDOM_STRING_LENGTH
        bits_needed = key_length * 4  # Each hex char = 4 bits
        all_keys = [
            format(random.getrandbits(bits_needed), f"0{key_length}x")
            for _ in range(total_items)
        ]

        # Pre-allocate array with None slots (will be filled with {key, index} objects)
        matched_entries = [None] * total_items
        all_pages_data = []

        # Process each page with unique incremental indices per item (term + definition distinct)
        global_counter = 0
        for _, page_cards in enumerate(pages):
            left_items = []
            right_items = []

            for card in page_cards:
                # Generate term item
                term_index = global_counter
                term_key = all_keys[term_index]
                term_text = card.get("term", "")
                left_items.append({"text": term_text, "index": term_index})
                global_counter += 1

                # Generate definition item
                def_index = global_counter
                def_key = all_keys[def_index]
                def_text = card.get("definition", "")
                right_items.append({"text": def_text, "index": def_index})
                global_counter += 1

                # Add bidirectional mapping entries as UUID-like strings for obfuscation
                matched_entries[term_index] = CommonHandlers.format_as_uuid_like(
                    term_key, def_index
                )
                matched_entries[def_index] = CommonHandlers.format_as_uuid_like(
                    def_key, term_index
                )

            # Shuffle left and right items per page if enabled
            if xblock.is_shuffled:
                random.shuffle(left_items)
                random.shuffle(right_items)

            all_pages_data.append(
                {"left_items": left_items, "right_items": right_items}
            )

        encryption_key = CommonHandlers.generate_encryption_key(xblock)
        encrypted_hash = CommonHandlers.encrypt_data(matched_entries, encryption_key)

        # Include all pages data in payload; encrypted "key" now holds list of pairs
        mapping_payload = {"key": encrypted_hash, "pages": all_pages_data}
        encoded_mapping = base64.b64encode(
            json.dumps(mapping_payload).encode()
        ).decode()

        total_pages = len(pages)

        template_context = {
            "title": getattr(xblock, "title", DEFAULT.MATCHING_TITLE),
            "list_length": list_length,
            "all_pages": all_pages_data,
            "has_timer": getattr(xblock, "has_timer", DEFAULT.HAS_TIMER),
            "total_pages": total_pages,
        }

        var_names = CommonHandlers.generate_unique_var_names(
            ["runtime", "elem", "tag", "payload", "err"], min_len=1, max_len=3
        )

        data_element_id = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=16)
        )

        # Generate unique function name per XBlock to avoid conflicts
        init_function_name = "MatchingInit_" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )

        runtime = var_names["runtime"]
        elem = var_names["elem"]
        payload = var_names["payload"]

        # Build obfuscated decoder function; initializes JS via payload
        obf_decoder = (
            f"function {init_function_name}({var_names['runtime']},{var_names['elem']}){{"
            f"var {var_names['tag']}=$('#{data_element_id}',{var_names['elem']});"
            f"if(!{var_names['tag']}.length)return;try{{"
            f"var {var_names['payload']}=JSON.parse(atob({var_names['tag']}.text()));"
            f"{var_names['tag']}.remove();if({var_names['payload']}&&{var_names['payload']}.pages)"
            f"GamesXBlockMatchingInit({runtime},{elem},{payload}.pages,{payload}.key);"
            f"$('#obf_decoder_script',{var_names['elem']}).remove();"
            f"}}catch({var_names['err']}){{console.warn('Decode failed');}}}}"
        )

        template_context["encoded_mapping"] = encoded_mapping
        template_context["obf_decoder"] = obf_decoder
        template_context["data_element_id"] = data_element_id
        template_context["init_function_name"] = init_function_name

        template_str = pkg_resources.resource_string(
            __name__, "../static/html/matching.html"
        ).decode("utf8")
        template = Template(template_str)
        html = template.render(Context(template_context))

        frag = Fragment(html)
        frag.add_css(
            pkg_resources.resource_string(
                __name__, "../static/css/matching.css"
            ).decode("utf8")
        )
        frag.add_css(
            pkg_resources.resource_string(
                __name__, "../static/css/confetti.css"
            ).decode("utf8")
        )
        frag.add_javascript(
            pkg_resources.resource_string(
                __name__, "../static/js/src/matching.js"
            ).decode("utf8")
        )
        frag.add_javascript(
            pkg_resources.resource_string(
                __name__, "../static/js/src/confetti.js"
            ).decode("utf8")
        )
        frag.initialize_js(init_function_name)
        return frag

    @staticmethod
    def get_matching_key_mapping(xblock, data, suffix=""):
        """Decrypt and return the key mapping for matching game validation."""
        try:
            matching_key = data.get("matching_key")
            if not matching_key:
                return {"success": False, "error": "Missing matching_key parameter"}

            encryption_key = CommonHandlers.generate_encryption_key(xblock)
            key_mapping = CommonHandlers.decrypt_data(matching_key, encryption_key)

            return {"success": True, "data": key_mapping, "mode": xblock.get_mode()}
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {"success": False, "error": f"Failed to decrypt mapping: {str(e)}"}

    @staticmethod
    def refresh_game(xblock, request, suffix=""):
        """Refresh the game view with new shuffled data."""
        frag = MatchingHandlers.student_view(xblock, context=None)

        return Response(frag.content, content_type="text/html", charset="UTF-8")

    @staticmethod
    def complete_matching_game(xblock, data, suffix=""):
        """Complete the matching game and compare the user's time to the best_time field."""
        new_time = data["new_time"]
        prev_best_time = xblock.best_time

        if prev_best_time is None or new_time < prev_best_time:
            xblock.best_time = new_time

        return {
            "new_time": new_time,
            "prev_best_time": prev_best_time,
        }
