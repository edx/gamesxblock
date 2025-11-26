"""
Common handler methods for the Games XBlock.
"""

import hashlib
import random
import string
import uuid

from django.core.files.base import ContentFile
from django.utils.translation import gettext as _
from xblock.core import Response
from xblock.fields import Set, Dict

from games.utils import delete_image, get_gamesxblock_storage

from ..constants import CARD_FIELD, DEFAULT, GAME_TYPE, UPLOAD


class CommonHandlers:
    """Handlers that work across all game types."""

    @staticmethod
    def generate_unique_var_names(keys, min_len=3, max_len=6, max_attempts=1000):
        """
        Generate unique random variable names for obfuscation.
        """
        used = set()
        names = {}
        for key in keys:
            for _ in range(max_attempts):
                name = "".join(random.choices(string.ascii_lowercase, k=random.randint(min_len, max_len)))
                if name not in used:
                    used.add(name)
                    names[key] = name
                    break
            else:
                raise RuntimeError(f"Unable to generate a unique variable name after {max_attempts} attempts. Consider increasing min_len/max_len.")
        return names

    @staticmethod
    def generate_unique_alphanumeric_key(existing_keys=None, key_length=6):
        """
        Generate a unique alphanumeric key of specified length.
        
        Args:
            existing_keys: Set of keys to check for uniqueness. If None, uniqueness is not enforced.
            key_length: Length of the key to generate (default: 6).
        
        Returns:
            A unique alphanumeric string of the specified length.
        """
        if existing_keys is None:
            existing_keys = set()
        
        while True:
            key = "".join(random.choices(string.ascii_letters + string.digits, k=key_length))
            if key not in existing_keys:
                return key

    @staticmethod
    def expand_game(xblock, data, suffix=""):
        """A handler to expand the game from its title block."""
        description = _("ERR: self.game_type not defined or invalid")
        if xblock.game_type == GAME_TYPE.FLASHCARDS:
            description = _("Click each card to reveal the definition")
        elif xblock.game_type == GAME_TYPE.MATCHING:
            description = _("Match each term with the correct definition")
        return {
            "title": xblock.title,
            "description": description,
            "game_type": xblock.game_type,
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
        """
        Upload an image file to configured storage (S3 if set) and return URL.
        """
        asset_storage = get_gamesxblock_storage()
        try:
            upload_file = request.params["file"].file
            file_name = request.params["file"].filename
            if "." not in file_name:
                return Response(
                    json_body={
                        "success": False,
                        "error": "File must have an extension",
                    },
                    status=400,
                )
            _, ext = file_name.rsplit(".", 1)
            ext = ext.lower()
            allowed_exts = ["jpg", "jpeg", "png", "gif", "webp", "svg"]
            if ext not in allowed_exts:
                return Response(
                    json_body={
                        "success": False,
                        "error": f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(allowed_exts))}",
                    },
                    status=400,
                )
            blob = upload_file.read()
            file_hash = hashlib.md5(blob).hexdigest()
            file_path = f"{UPLOAD.PATH_PREFIX}/{xblock.scope_ids.usage_id.block_id}/{file_hash}.{ext}"
            saved_path = asset_storage.save(file_path, ContentFile(blob))
            file_url = asset_storage.url(saved_path)
            return Response(
                json_body={
                    "success": True,
                    "url": file_url,
                    "filename": file_name,
                    "file_path": file_path,
                }
            )
        except Exception as e:
            return Response(json_body={"success": False, "error": str(e)}, status=400)

    @staticmethod
    def delete_image_handler(self, data, suffix=""):
        """
        Delete an image by storage key.
        Expected: { "key": "gamesxblock/<block_id>/<hash>.ext" }
        """
        key = data.get("key")
        if not key:
            return {"success": False, "error": "Missing key"}
        try:
            is_deleted = delete_image(self.asset_storage, key)
            return {"success": is_deleted, "key": key}
        except Exception as e:
            return {"success": False, "error": str(e)}

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
                if not isinstance(card, Dict):
                    return {"success": False, "error": _("Each card must be an object")}

                # Validate required fields
                if CARD_FIELD.TERM not in card or CARD_FIELD.DEFINITION not in card:
                    return {
                        "success": False,
                        "error": _("Each card must have term and definition"),
                    }

                validated_cards.append(
                    {
                        CARD_FIELD.TERM: card.get(CARD_FIELD.TERM, ""),
                        CARD_FIELD.TERM_IMAGE: card.get(CARD_FIELD.TERM_IMAGE, ""),
                        CARD_FIELD.DEFINITION: card.get(CARD_FIELD.DEFINITION, ""),
                        CARD_FIELD.DEFINITION_IMAGE: card.get(
                            CARD_FIELD.DEFINITION_IMAGE, ""
                        ),
                        CARD_FIELD.ORDER: card.get(CARD_FIELD.ORDER, ""),
                        CARD_FIELD.CARD_KEY: card.get(
                            CARD_FIELD.CARD_KEY, str(uuid.uuid4())
                        ),
                    }
                )

            if new_game_type == GAME_TYPE.FLASHCARDS:
                xblock.title = DEFAULT.FLASHCARDS_TITLE
            else:
                xblock.title = DEFAULT.MATCHING_TITLE
            xblock.cards = validated_cards
            xblock.game_type = new_game_type
            xblock.is_shuffled = new_is_shuffled
            xblock.list_length = len(validated_cards)

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
    def close_game(xblock, data, suffix=""):
        """A handler to close the game to its title block."""
        xblock.game_started = False
        xblock.time_seconds = 0
        xblock.match_count = 0
        xblock.matches_remaining = xblock.list_length

        if xblock.game_type == GAME_TYPE.FLASHCARDS:
            xblock.term_is_visible = True
            xblock.list_index = 0
        return {"title": xblock.title}
