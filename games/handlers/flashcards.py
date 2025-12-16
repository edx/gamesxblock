"""
Flashcards game handler methods.
"""

import random
import base64
import json
import string

import pkg_resources
from django.template import Context, Template
from web_fragments.fragment import Fragment

from ..constants import CARD_FIELD, CONFIG, DEFAULT
from .common import CommonHandlers


class FlashcardsHandlers:
    """Handlers specific to the flashcards game."""

    @staticmethod
    def student_view(xblock, context=None):
        """
        The student view for flashcards game.
        """
        cards = list(xblock.cards) if xblock.cards else []
        list_length = len(cards)

        if xblock.is_shuffled and cards:
            random.shuffle(cards)

        # Build payload with salt for light obfuscation (pattern similar to matching)
        salt = "".join(random.choices(string.ascii_letters + string.digits, k=CONFIG.SALT_LENGTH))
        payload_cards = []
        for card in cards:
            payload_cards.append(
                {
                    "id": card.get(CARD_FIELD.CARD_KEY, ""),
                    "term": card.get(CARD_FIELD.TERM, ""),
                    "definition": card.get(CARD_FIELD.DEFINITION, ""),
                    "term_image": card.get(CARD_FIELD.TERM_IMAGE, ""),
                    "definition_image": card.get(CARD_FIELD.DEFINITION_IMAGE, ""),
                }
            )
        mapping_payload = {"cards": payload_cards, "salt": salt}
        encoded_mapping = base64.b64encode(json.dumps(mapping_payload).encode()).decode()

        # Random variable names for light obfuscation
        var_names = CommonHandlers.generate_unique_var_names(
            ["runtime", "elem", "tag", "payload", "err"], min_len=3, max_len=6
        )

        # Unique id for embedded data element (script tag)
        data_element_id = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=16)
        )

        # Generate unique function name per XBlock to avoid conflicts
        init_function_name = "FlashcardsInit_" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )

        # Obfuscated decoder with unique function name
        obf_decoder = (
            f"function {init_function_name}({var_names['runtime']},{var_names['elem']}){{"  # function header
            f"var {var_names['tag']}=$('#{data_element_id}',{var_names['elem']});"  # locate script tag
            f"if(!{var_names['tag']}.length)return;try{{"  # guard
            f"var {var_names['payload']}=JSON.parse(atob({var_names['tag']}.text()));"  # decode
            f"{var_names['tag']}.remove();"  # remove script
            f"if({var_names['payload']}&&{var_names['payload']}.cards)"  # validate
            f"GamesXBlockFlashcardsInit({var_names['runtime']},{var_names['elem']},{var_names['payload']}.cards);"  # init
            f"}}catch({var_names['err']}){{console.warn('Decode failed');}}}}"
        )

        template_context = {
            "title": getattr(xblock, "title", DEFAULT.FLASHCARDS_TITLE),
            "list_length": list_length,
            "encoded_mapping": encoded_mapping,
            "obf_decoder": obf_decoder,
            "data_element_id": data_element_id,
        }

        template_str = pkg_resources.resource_string(
            __name__, "../static/html/flashcards.html"
        ).decode("utf8")
        template = Template(template_str)
        html = template.render(Context(template_context))

        frag = Fragment(html)
        frag.add_css(
            pkg_resources.resource_string(__name__, "../static/css/flashcards.css").decode(
                "utf8"
            )
        )
        frag.add_javascript(
            pkg_resources.resource_string(
                __name__, "../static/js/src/flashcards.js"
            ).decode("utf8")
        )
        frag.initialize_js(init_function_name)
        return frag
