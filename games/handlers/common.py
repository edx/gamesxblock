"""
Common handler methods for the Games XBlock.
"""

import base64
import hashlib
import json
import random
import string
import uuid

from django.core.files.base import ContentFile
from django.utils.translation import gettext as _
from xblock.core import Response
from cryptography.fernet import Fernet

from games.utils import delete_image, get_gamesxblock_storage

from ..constants import CARD_FIELD, CONFIG, DEFAULT, GAME_TYPE, UPLOAD


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
    def generate_encryption_key(xblock):
        """
        Generate encryption key using block_id and salt.
        Uses a consistent identifier that doesn't change across requests.

        Args:
            xblock: The xblock instance

        Returns:
            Base64-encoded encryption key (bytes)
        """
        # Use block_id (which is stable) and the encryption salt
        block_id = str(xblock.scope_ids.usage_id.block_id)
        seed_string = f"{block_id}:{CONFIG.ENCRYPTION_SALT}"

        # Generate a 32-byte key using SHA-256
        key_bytes = hashlib.sha256(seed_string.encode()).digest()

        # Fernet requires base64-encoded 32-byte key
        return base64.urlsafe_b64encode(key_bytes)

    @staticmethod
    def encrypt_data(data, encryption_key):
        """
        Encrypt data using Fernet (symmetric encryption).

        Args:
            data: Dictionary or any JSON-serializable data to encrypt
            encryption_key: Base64-encoded encryption key

        Returns:
            Base64-encoded encrypted string
        """
        fernet = Fernet(encryption_key)
        data_json = json.dumps(data)
        encrypted_data = fernet.encrypt(data_json.encode())
        return encrypted_data.decode()

    @staticmethod
    def decrypt_data(encrypted_hash, encryption_key):
        """
        Decrypt encrypted data back to original format.

        Args:
            encrypted_hash: Base64-encoded encrypted string
            encryption_key: Base64-encoded encryption key

        Returns:
            Decrypted data (dictionary or original data structure)
        """
        fernet = Fernet(encryption_key)
        # Fernet.decrypt expects bytes (base64-encoded), so just encode the string
        decrypted_json = fernet.decrypt(encrypted_hash.encode()).decode()
        return json.loads(decrypted_json)

    @staticmethod
    def get_settings(xblock, data, suffix=""):
        """Get game type, cards, and shuffle setting in one call."""
        return {
            "game_type": xblock.game_type,
            "cards": xblock.cards,
            "is_shuffled": xblock.is_shuffled,
            "has_timer": xblock.has_timer,
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
            storage = get_gamesxblock_storage()
            is_deleted = delete_image(storage, key)
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
            'has_timer': true or false,
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
            new_has_timer = data.get("has_timer", DEFAULT.HAS_TIMER)
            new_cards = data.get("cards", [])
            display_name = data.get("display_name", DEFAULT.DISPLAY_NAME)

            validated_cards = []
            for card in new_cards:
                if not isinstance(card, dict):
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

            xblock.display_name = display_name
            if new_game_type == GAME_TYPE.FLASHCARDS:
                xblock.title = DEFAULT.FLASHCARDS_TITLE
            else:
                xblock.title = DEFAULT.MATCHING_TITLE
            xblock.cards = validated_cards
            xblock.game_type = new_game_type
            xblock.is_shuffled = new_is_shuffled
            xblock.has_timer = new_has_timer
            xblock.list_length = len(validated_cards)

            xblock.save()

            return {
                "success": True,
                "game_type": xblock.game_type,
                "cards": xblock.cards,
                "count": len(xblock.cards),
                "is_shuffled": xblock.is_shuffled,
                "has_timer": xblock.has_timer,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def format_as_uuid_like(key_hex, index):
        """
        Format key and index as UUID-like string for maximum obfuscation.
        Format: key-index_part1-rand4-index_part2-rand12

        Args:
            key_hex: 8-char hex string (key)
            index: integer index

        Returns:
            UUID-like formatted string (36 chars total: 8-4-4-4-12)
        """
        index_hex = format(index, '08x')
        index_part1 = index_hex[:4]
        index_part2 = index_hex[4:]
        rand_4 = format(random.getrandbits(16), '04x')
        rand_12 = format(random.getrandbits(48), '012x')
        return f"{key_hex}-{index_part1}-{rand_4}-{index_part2}-{rand_12}"
