"""An XBlock providing gamification capabilities."""

import hashlib

import pkg_resources
from django.core.files.base import ContentFile

from django.core.files.storage import default_storage
from web_fragments.fragment import Fragment
from xblock.core import Response, XBlock
from xblock.fields import Boolean, List, Scope, String


class GamesXBlock(XBlock):
    """
    An XBlock for creating interactive games with flashcards and matching.
    """

    display_name = String(
        default="Games", scope=Scope.settings, help="Display name for this XBlock"
    )

    game_type = String(
        default="flashcards",
        scope=Scope.settings,
        help="The type of game: 'flashcards' or 'matching'",
    )

    cards = List(
        default=[],
        scope=Scope.content,
        help="List of cards with term, term_image, definition, definition_image",
    )

    is_shuffled = Boolean(
        default=False, scope=Scope.settings, help="Whether the cards should be shuffled"
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the GamesXBlock, shown to students.
        """
        html = self.resource_string("static/html/games.html")
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/games.css"))
        frag.add_javascript(self.resource_string("static/js/src/games.js"))
        frag.initialize_js("GamesXBlock")
        return frag

    @XBlock.json_handler
    def get_settings(self, data, suffix=""):
        """
        Get game type, cards, and shuffle setting in one call.
        """
        return {
            "game_type": self.game_type,
            "cards": self.cards,
            "is_shuffled": self.is_shuffled,
        }

    @XBlock.handler
    def upload_image(self, request, suffix=""):
        """
        Upload an image file and return the URL.
        """
        try:
            upload_file = request.params["file"].file
            file_name = request.params["file"].filename

            file_hash = hashlib.md5(upload_file.read()).hexdigest()
            upload_file.seek(0)

            _, ext = (
                file_name.rsplit(".", 1) if "." in file_name else (file_name, "jpg")
            )

            file_path = f"games/{self.scope_ids.usage_id.block_id}/{file_hash}.{ext}"

            saved_path = default_storage.save(
                file_path, ContentFile(upload_file.read())
            )

            file_url = default_storage.url(saved_path)

            return Response(
                json_body={"success": True, "url": file_url, "filename": file_name}
            )

        except Exception as e:
            return Response(json_body={"success": False, "error": str(e)}, status=400)

    @XBlock.json_handler
    def save_settings(self, data, suffix=""):
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
            new_game_type = data.get("game_type", "flashcards")
            new_is_shuffled = data.get("is_shuffled", False)
            new_cards = data.get("cards", [])

            validated_cards = []
            for card in new_cards:
                if not isinstance(card, dict):
                    return {"success": False, "error": "Each card must be an object"}

                # Validate required fields
                if "term" not in card or "definition" not in card:
                    return {
                        "success": False,
                        "error": "Each card must have term and definition",
                    }

                validated_cards.append(
                    {
                        "term": card.get("term", ""),
                        "term_image": card.get("term_image", ""),
                        "definition": card.get("definition", ""),
                        "definition_image": card.get("definition_image", ""),
                        "order": card.get("order", ""),
                    }
                )

            self.cards = validated_cards
            self.game_type = new_game_type
            self.is_shuffled = new_is_shuffled

            self.save()

            return {
                "success": True,
                "game_type": self.game_type,
                "cards": self.cards,
                "count": len(self.cards),
                "is_shuffled": self.is_shuffled,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            (
                "GamesXBlock",
                """<vertical_demo>
                <games/>
                </vertical_demo>
             """,
            )
        ]
