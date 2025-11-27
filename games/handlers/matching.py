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
from ..constants import CONFIG, CONTAINER_TYPE, DEFAULT
from .common import CommonHandlers


class MatchingHandlers:

    @staticmethod
    def student_view(xblock, context=None):
        # Prepare and optionally shuffle cards
        cards = list(xblock.cards) if xblock.cards else []
        if xblock.is_shuffled and cards:
            random.shuffle(cards)

        list_length = len(cards)

        existing_keys = set()
        key_mapping = {}
        left_items = []
        right_items = []

        for idx, card in enumerate(cards):
            term_key = CommonHandlers.generate_unique_alphanumeric_key(existing_keys)
            existing_keys.add(term_key)
            term_text = card.get("term", "")
            key_mapping[term_key] = {"value": term_text, "pair_id": idx}

            left_items.append({term_key: term_text})

            def_key = CommonHandlers.generate_unique_alphanumeric_key(existing_keys)
            existing_keys.add(def_key)
            def_text = card.get("definition", "")
            key_mapping[def_key] = {"value": def_text, "pair_id": idx}

            right_items.append({def_key: def_text})

        if xblock.is_shuffled and cards:
            all_items = left_items + right_items
            random.shuffle(all_items)
            left_items = all_items[:list_length]
            right_items = all_items[list_length:]

        encryption_key = CommonHandlers.generate_encryption_key(xblock)
        encrypted_hash = CommonHandlers.encrypt_data(key_mapping, encryption_key)

        flat_items_for_js = left_items + right_items
        mapping_payload = {"key": encrypted_hash, "pairs": flat_items_for_js}

        for i, item in enumerate(left_items):
            for key in item:
                left_items[i] = {"key": key, "text": item[key], "index": i}
        for i, item in enumerate(right_items):
            for key in item:
                right_items[i] = {"key": key, "text": item[key], "index": i + list_length}
        encoded_mapping = base64.b64encode(
            json.dumps(mapping_payload).encode()
        ).decode()

        template_context = {
            "title": getattr(xblock, "title", DEFAULT.MATCHING_TITLE),
            "list_length": list_length,
            "left_items": left_items,
            "right_items": right_items,
        }

        # Legacy mapping for backward compatibility (salted, base64)
        salt = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        pairs = []
        for card in cards:
            pairs.append({"t": card.get("term", ""), "d": card.get("definition", "")})
        mapping_payload = {"pairs": pairs, "salt": salt}
        old_encoded_mapping = base64.b64encode(
            json.dumps(mapping_payload).encode()
        ).decode()

        var_names = CommonHandlers.generate_unique_var_names(
            ["runtime", "elem", "tag", "payload", "err"], min_len=1, max_len=3
        )

        data_element_id = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=16)
        )

        # Build obfuscated decoder function; initializes JS via payload
        obf_decoder = (
            f"function MatchingInit({var_names['runtime']},{var_names['elem']}){{"
            f"var {var_names['tag']}=$('#{data_element_id}',{var_names['elem']});"
            f"if(!{var_names['tag']}.length)return;try{{"
            f"var {var_names['payload']}=JSON.parse(atob({var_names['tag']}.text()));"
            f"{var_names['tag']}.remove();if({var_names['payload']}&&{var_names['payload']}.pairs)"
            f"GamesXBlockMatchingInit({var_names['runtime']},{var_names['elem']},{var_names['payload']}.pairs,{var_names['payload']}.key);"
            f"$('#obf_decoder_script',{var_names['elem']}).remove();"
            f"}}catch({var_names['err']}){{console.warn('Decode failed');}}}}"
        )

        template_context["encoded_mapping"] = encoded_mapping
        template_context["obf_decoder"] = obf_decoder
        template_context["data_element_id"] = data_element_id

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
        frag.initialize_js("MatchingInit")
        return frag

    @staticmethod
    def _random_string():
        return str(
            "".join(random.choices(string.ascii_letters, k=CONFIG.RANDOM_STRING_LENGTH))
        )

    @staticmethod
    def get_matching_key_mapping(xblock, data, suffix=""):
        try:
            matching_key = data.get("matching_key")
            if not matching_key:
                return {
                    "success": False,
                    "error": "Missing matching_key parameter"
                }

            encryption_key = CommonHandlers.generate_encryption_key(xblock)
            key_mapping = CommonHandlers.decrypt_data(matching_key, encryption_key)

            return {
                "success": True,
                "data": key_mapping
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to decrypt mapping: {str(e)}"
            }

    @staticmethod
    def refresh_game(xblock, request, suffix=""):
        frag = MatchingHandlers.student_view(xblock, context=None)

        return Response(
            frag.content,
            content_type='text/html',
            charset='UTF-8'
        )

    @staticmethod
    def complete_matching_game(xblock, data, suffix=""):
        new_time = data["new_time"]
        prev_best_time = xblock.best_time

        if prev_best_time is None or new_time < prev_best_time:
            xblock.best_time = new_time

        return {
            "new_time": new_time,
            "prev_best_time": prev_best_time,
        }
