"""An XBlock providing gamification capabilities."""

import hashlib
import random
import string

import pkg_resources
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from web_fragments.fragment import Fragment
from xblock.core import Response, XBlock
from xblock.fields import Boolean, Dict, Integer, List, Scope, String


class GamesXBlock(XBlock):
    """
    An XBlock for creating games.

    The Student view will display the game content and allow the student to interact
    accordingly.

    The editor view will allow course authors to create and manipulate the games.
    """

    title = String(
        default="Matching",
        scope=Scope.content,
        help="The title of the block to be displayed in the xblock.",
    )
    display_name = String(
        default="Games", scope=Scope.settings, help="Display name for this XBlock"
    )

    # Change default to 'matching' for matching game and 'flashcards' for flashcards game to test
    game_type = String(
        default="matching",
        scope=Scope.settings,
        help="The kind of game this xblock is responsible for ('flashcards' or 'matching' for now).",
    )

    cards = List(
        default=[], scope=Scope.content, help="The list of terms and definitions."
    )

    list_length = Integer(
        default=len(cards.default),
        scope=Scope.content,
        help="A field for the length of the list for convenience.",
    )

    # Flashcard game fields------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    list_index = Integer(
        default=0,
        scope=Scope.user_state,
        help="Current flashcard index for user",
    )

    matching_id_dictionary_index = Dict(
        default={},
        scope=Scope.user_state,
        help="A dictionary to encrypt the ids of the terms and definitions for the matching game.",
    )

    matching_id_dictionary_type = Dict(
        default={},
        scope=Scope.user_state,
        help="A dictionary to tie the id to the type of container (term or definition) for the matching game.",
    )

    matching_id_dictionary = Dict(
        default={},
        scope=Scope.user_state,
        help="A dictionary to encrypt the ids of the terms and definitions for the matching game.",
    )

    match_count = Integer(
        default=0,
        scope=Scope.user_state,
        help="Tracks how many matches have been successfully made. Used to determine when to switch pages.",
    )

    matches_remaining = Integer(
        default=0, scope=Scope.user_state, help="The number of matches remaining."
    )

    selected_containers = Dict(
        default={},
        scope=Scope.user_state,
        help="A dictionary to keep track of selected containers for the matching game.",
    )

    is_shuffled = Boolean(
        default=False, scope=Scope.settings, help="Whether the cards should be shuffled"
    )

    """
    #Following fields for editor only------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    timer = Boolean(
        default=True, 
        scope=Scope.settings, 
        help="Whether to enable the timer for the matching game."
    )
    """

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the GamesXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/games.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/games.css"))
        frag.add_javascript(self.resource_string("static/js/src/games.js"))
        frag.initialize_js("GamesXBlock")
        return frag

    # Universal handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @XBlock.json_handler
    def expand_game(self, data, suffix=""):
        """
        A handler to expand the game from its title block.
        """
        description = "ERR: self.game_type not defined or invalid"
        if self.game_type == "flashcards":
            description = "Click each card to reveal the definition"
        elif self.game_type == "matching":
            description = "Match each term with the correct definition"
        return {
            "title": self.title,
            "description": description,
            "game_type": self.game_type,
        }

    @XBlock.json_handler
    def get_settings(self, data, suffix=""):
        """
        A handler to get settings.
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

            game_type_changed_to_matching = (
                self.game_type == "flashcards" and new_game_type == "matching"
            )

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

                if game_type_changed_to_matching:
                    validated_cards.append(
                        {
                            "term": card.get("term", ""),
                            "term_image": "",
                            "definition": card.get("definition", ""),
                            "definition_image": "",
                        }
                    )
                else:
                    validated_cards.append(
                        {
                            "term": card.get("term", ""),
                            "term_image": card.get("term_image", ""),
                            "definition": card.get("definition", ""),
                            "definition_image": card.get("definition_image", ""),
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

    @XBlock.json_handler
    def close_game(self, data, suffix=""):
        """
        A handler to close the game to its title block.
        """
        cards_length = len(self.cards) if self.cards else 0
        self.match_count = 0
        self.matches_remaining = cards_length

        return {"title": self.title}

    @XBlock.json_handler
    def display_help(self, data, suffix=""):
        """
        A handler to display a tooltip message above the help icon.
        """
        message = "ERR: self.game_type not defined or invalid"
        if self.game_type == "flashcards":
            message = "Click each card to reveal the definition"
        elif self.game_type == "matching":
            message = "Match each term with the correct definition"
        return {"message": message}

    # Flashcards handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @XBlock.json_handler
    def start_game_flashcards(self, data, suffix=""):
        """
        A handler to begin the flashcards game.
        Returns all cards, shuffled if is_shuffled is enabled.
        """
        cards_to_return = self.cards.copy() if self.cards else []

        if self.is_shuffled and cards_to_return:
            random.shuffle(cards_to_return)

        return {"cards": cards_to_return, "cards_length": len(cards_to_return)}

    # Matching handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @XBlock.json_handler
    def start_game_matching(self, data, suffix=""):
        """
        A handler to begin the matching game.
        Returns all cards with term and definition (no images for matching).
        Shuffles if is_shuffled is enabled.
        """

        # function to return a random ascii string of 6 characters (upper- and lower-case)
        def randomString():
            return str("".join(random.choices(string.ascii_letters, k=6)))

        cards_to_use = self.cards.copy() if self.cards else []
        cards_length = len(cards_to_use)

        # Shuffle if enabled
        if self.is_shuffled and cards_to_use:
            random.shuffle(cards_to_use)

        # Create temporary dictionaries for this game session (don't save to fields)
        matching_id_dictionary_index = {}
        matching_id_dictionary_type = {}
        matching_id_dictionary = {}
        matching_id_list = []

        # create dictionaries and key-value pairs to reference the cards based on ids that will be sent to games.js
        for i in range(0, 2 * cards_length, 2):
            # the ids are random strings stored into an indexed list
            uniqueString = randomString()
            while uniqueString in matching_id_list:
                uniqueString = randomString()
            matching_id_list.append(uniqueString)  # append id at index i

            uniqueString = randomString()
            while uniqueString in matching_id_list:
                uniqueString = randomString()
            matching_id_list.append(uniqueString)  # append id at index i+1

            # the random string ids are the dictionary keys for the indices, types, and container content that they reference in the cards
            matching_id_dictionary_index[matching_id_list[i]] = i // 2
            matching_id_dictionary_index[matching_id_list[i + 1]] = i // 2

            matching_id_dictionary_type[matching_id_list[i]] = "term"
            matching_id_dictionary_type[matching_id_list[i + 1]] = "definition"

            matching_id_dictionary[matching_id_list[i]] = cards_to_use[i // 2]["term"]
            matching_id_dictionary[matching_id_list[i + 1]] = cards_to_use[i // 2][
                "definition"
            ]

        # Store the dictionaries for this session
        self.matching_id_dictionary_index = matching_id_dictionary_index
        self.matching_id_dictionary_type = matching_id_dictionary_type
        self.matching_id_dictionary = matching_id_dictionary

        return {
            "cards": cards_to_use,
            "cards_length": cards_length,
            "id_dictionary_index": matching_id_dictionary_index,
            "id_dictionary": matching_id_dictionary,
            "id_list": matching_id_list,
            "time": "0:00",
        }

    @XBlock.json_handler
    def select_container(self, data, suffix=""):
        """
        A handler for selecting matching game containers and evaluating matches.
        """
        cards_length = len(self.cards) if self.cards else 0

        # add a '#' to id for use with jQuery (this could be done in the js file as well)
        id = "#" + data["id"]
        container_type = self.matching_id_dictionary_type[data["id"]]
        index = self.matching_id_dictionary_index[data["id"]]

        # if no container is selected yet
        if len(self.selected_containers) == 0:
            self.selected_containers["container1_id"] = id
            self.selected_containers["container1_type"] = container_type
            self.selected_containers["container1_index"] = index
            return {
                "first_selection": True,
                "deselect": False,
                "id": id,
                "prev_id": None,
                "match": False,
                "match_count": self.match_count,
                "matches_remaining": self.matches_remaining,
                "cards": self.cards,
                "cards_length": cards_length,
                "id_dictionary": self.matching_id_dictionary,
            }

        # else

        # establish prev_id before conditionals since the selected_containers dictionary is cleared before returning to js
        prev_id = self.selected_containers["container1_id"]

        # if the container referenced by 'id' is already selected, deselect it
        if id == self.selected_containers["container1_id"]:
            self.selected_containers.clear()
            return {
                "first_selection": False,
                "deselect": True,
                "id": id,
                "prev_id": prev_id,
                "match": False,
                "match_count": self.match_count,
                "matches_remaining": self.matches_remaining,
                "cards": self.cards,
                "cards_length": cards_length,
                "id_dictionary": self.matching_id_dictionary,
            }

        # containers with the same game_type cannot match (i.e. a term with a term, etc.)
        if container_type == self.selected_containers["container1_type"]:
            self.selected_containers.clear()
            return {
                "first_selection": False,
                "deselect": False,
                "id": id,
                "prev_id": prev_id,
                "match": False,
                "match_count": self.match_count,
                "matches_remaining": self.matches_remaining,
                "cards": self.cards,
                "cards_length": cards_length,
                "id_dictionary": self.matching_id_dictionary,
            }

        # if the execution gets to this point and the indices are the same, this implies a term/ definition match
        if index == self.selected_containers["container1_index"]:
            self.selected_containers.clear()
            self.match_count += 1
            self.matches_remaining -= 1
            return {
                "first_selection": False,
                "deselect": False,
                "id": id,
                "prev_id": prev_id,
                "match": True,
                "match_count": self.match_count,
                "matches_remaining": self.matches_remaining,
                "cards": self.cards,
                "cards_length": cards_length,
                "id_dictionary": self.matching_id_dictionary,
            }

        # not a match
        self.selected_containers.clear()
        return {
            "first_selection": False,
            "deselect": False,
            "id": id,
            "prev_id": prev_id,
            "match": False,
            "match_count": self.match_count,
            "matches_remaining": self.matches_remaining,
            "cards": self.cards,
            "cards_length": cards_length,
            "id_dictionary": self.matching_id_dictionary,
        }

    @XBlock.json_handler
    def end_game_matching(self, data, suffix=""):
        """
        A handler to end the matching game.
        """
        cards_length = len(self.cards) if self.cards else 0
        self.selected_containers = {}
        self.match_count = 0
        self.matches_remaining = cards_length

        return {"success": True}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            (
                "Multiple GamesXBlock",
                """<vertical_demo>
                <games/>
                <games/>
                <games/>
                </vertical_demo>
             """,
            ),
            (
                "games",
                """<games/>
              """,
            ),
        ]

    """
    @XBlock.json_handler
    def flip_timer(self, data, suffix=''):
        self.timer = not(self.timer)
        return {'timer': self.timer}

    @XBlock.json_handler
    def flip_shuffle(self, data, suffix=''):
        self.shuffle = not(self.shuffle)
        return {'shuffle': self.shuffle}
    """

    """
    # The following is another way to approach the list field - currently not used but may be useful after dummy data is no longer used.
        default=[
            Dict(
                default={'term': 'term1', 'definition': 'definition1'},
                scope=Scope.content,
                help="The first flashcard in the list."
            ),
            Dict(
                default={'term': 'term2', 'definition': 'definition2'},
                scope=Scope.content,
                help="The second flashcard in the list."
            ),
            Dict(
                default={'term': 'term3', 'definition': 'definition3'},
                scope=Scope.content,
                help="The third flashcard in the list."
            )
        ],
        """
    # )
