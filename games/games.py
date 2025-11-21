"""An XBlock providing gamification capabilities."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Boolean, Dict, Integer, List, Scope, String

from .constants import DEFAULT
from .handlers import CommonHandlers, FlashcardsHandlers, MatchingHandlers

class GamesXBlock(XBlock):
    """
    An XBlock for creating games.

    The Student view will display the game content and allow the student to interact
    accordingly.

    The editor view will allow course authors to create and manipulate the games.
    """

    title = String(
        default=DEFAULT.TITLE,
        scope=Scope.content,
        help="The title of the block to be displayed in the xblock.",
    )
    display_name = String(
        default=DEFAULT.DISPLAY_NAME, scope=Scope.settings, help="Display name for this XBlock"
    )

    # Change default to 'matching' for matching game and 'flashcards' for flashcards game to test
    game_type = String(
        default=DEFAULT.GAME_TYPE,
        scope=Scope.settings,
        help="The kind of game this xblock is responsible for ('flashcards' or 'matching' for now).",
    )

    cards = List(
        default=[], scope=Scope.content, help="The list of terms and definitions."
    )

    # Alias for cards - handlers.py uses 'list' field name
    list = cards

    list_length = Integer(
        default=len(cards.default),
        scope=Scope.content,
        help="A field for the length of the list for convenience.",
    )

    # Flashcard game fields------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    term_is_visible = Boolean(
        default=True,
        scope=Scope.user_state,
        help="Whether the term side of the flashcard is currently visible.",
    )

    list_index = Integer(
        default=DEFAULT.LIST_INDEX,
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

    matching_id_list = List(
        default=[],
        scope=Scope.user_state,
        help="A list of random IDs for the matching game containers.",
    )

    game_started = Boolean(
        default=False,
        scope=Scope.user_state,
        help="Whether the matching game has started (for timer tracking).",
    )

    time_seconds = Integer(
        default=0,
        scope=Scope.user_state,
        help="Timer in seconds for the matching game.",
    )

    best_time = Integer(
        default=None,
        scope=Scope.user_state,
        help="Best time (in seconds) for completing the matching game.",
    )

    match_count = Integer(
        default=DEFAULT.MATCH_COUNT,
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
        default=DEFAULT.IS_SHUFFLED,
        scope=Scope.settings,
        help="Whether the cards should be shuffled",
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

    # Common handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @XBlock.json_handler
    def expand_game(self, data, suffix=''):
        """A handler to expand the game from its title block."""
        return CommonHandlers.expand_game(self, data, suffix)

    @XBlock.json_handler
    def get_settings(self, data, suffix=""):
        """Get game type, cards, and shuffle setting in one call."""
        return CommonHandlers.get_settings(self, data, suffix)

    @XBlock.handler
    def upload_image(self, request, suffix=""):
        """Upload an image file and return the URL."""
        return CommonHandlers.upload_image(self, request, suffix)

    @XBlock.json_handler
    def save_settings(self, data, suffix=""):
        """Save game type, shuffle setting, and all cards in one API call."""
        return CommonHandlers.save_settings(self, data, suffix)

    @XBlock.json_handler
    def close_game(self, data, suffix=''):
        """A handler to close the game to its title block."""
        return CommonHandlers.close_game(self, data, suffix)

    @XBlock.json_handler
    def display_help(self, data, suffix=''):
        """A handler to display a tooltip message above the help icon."""
        return CommonHandlers.display_help(self, data, suffix)

    # Flashcards handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @XBlock.json_handler
    def start_game_flashcards(self, data, suffix=''):
        """A handler to begin the flashcards game."""
        return FlashcardsHandlers.start_game_flashcards(self, data, suffix)

    @XBlock.json_handler
    def flip_flashcard(self, data, suffix=''):
        """A handler to flip the flashcard from term to definition and vice versa."""
        return FlashcardsHandlers.flip_flashcard(self, data, suffix)

    @XBlock.json_handler
    def page_turn(self, data, suffix=''):
        """A handler to turn the page to a new flashcard (left or right) in the list."""
        return FlashcardsHandlers.page_turn(self, data, suffix)

    # Matching handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @XBlock.json_handler
    def start_game_matching(self, data, suffix=''):
        """A handler to begin the matching game."""
        return MatchingHandlers.start_game_matching(self, data, suffix)

    @XBlock.json_handler
    def update_timer(self, data, suffix=''):
        """Update the timer. This is called every 1000ms by an ajax call."""
        return MatchingHandlers.update_timer(self, data, suffix)

    @XBlock.json_handler
    def select_container(self, data, suffix=''):
        """A handler for selecting matching game containers and evaluating matches."""
        return MatchingHandlers.select_container(self, data, suffix)

    @XBlock.json_handler
    def end_game_matching(self, data, suffix=''):
        """End the matching game and compare the user's time to the best_time field."""
        return MatchingHandlers.end_game_matching(self, data, suffix)

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
