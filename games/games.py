"""An XBlock providing gamification capabilities."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock

#May need to import more or less field types later (https://github.com/openedx/XBlock/blob/master/xblock/fields.py)
from xblock.fields import Integer, Scope, String, Boolean, List#, Dict

class GamesXBlock(XBlock):
    """
    An XBlock for creating games.

    The Student view will display the game content and allow the student to interact
    accordingly.

    The editor view will allow course authors to create and manipulate the games.
    """

    #Universal fields--------------------------------------------------------------
    title = String(
        default="Game Title", 
        scope=Scope.content, 
        help="The title of the block to be displayed in the xblock."
    )

    #Change default to 'matching' for matching game and 'flashcards' for flashcards game
    type = String(
        default="flashcards", 
        scope=Scope.settings, 
        help="The kind of game this xblock is responsible for ('flashcards' or 'matching' for now)."
    )

    #Matching and flashcards will use the same list, but term_image and definition_image will only be used in flashcards for now
    #DUMMY DATA
    list = List(
        default=[
            {
                'term_image': 'https://studio.stage.edx.org/static/studio/edx.org-next/images/studio-logo.005b2ebe0c8b.png',
                'definition_image': 'https://logos.openedx.org/open-edx-logo-tag.png',
                'term': 'Term 1', 
                'definition': 'The definition of term 1 (moderate character length).'
            },
            {
                'term_image': None, 
                'definition_image': None,
                'term': 'T2', 
                'definition': 'Def of T2 - short.'
            },
            {
                'term_image': 'https://logos.openedx.org/open-edx-logo-tag.png',
                'definition_image': 'https://studio.stage.edx.org/static/studio/edx.org-next/images/studio-logo.005b2ebe0c8b.png',
                'term': 'The Third Term', 
                'definition': 'The definition of term 3. This one is far longer for testing purposes, so long in fact that it should certainly warrant a new line.'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T4',
                'definition': 'D4'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T5',
                'definition': 'D5'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T6',
                'definition': 'D6'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T7',
                'definition': 'D7'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T8',
                'definition': 'D8'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T9',
                'definition': 'D9'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T10',
                'definition': 'D10'
            },
            {
                'term_image': None,
                'definition_image': None,
                'term': 'T11',
                'definition': 'D11'
            },
        ],
        scope=Scope.content,
        help="The list of terms and definitions."
    )

    list_length = Integer(
        default=len(list.default),
        scope=Scope.content,
        help="TEMP for HTML - WILL LIKELY NEED TO CHANGE WHEN DUMMY DATA IS NO LONGER USED"
    )

    #Flashcard game fields--------------------------------------------------------------
    list_index = Integer(
        default=0,
        scope=Scope.settings,
        help="Determines which flashcard from the list is currently visible."
    )

    term_is_visible = Boolean(
        default=True,
        scope=Scope.settings,
        help="True when the term is visible and false when the definition is visible in the flashcards game."
    )

    #Matching game fields--------------------------------------------------------------
    best_time = Integer(
        default=None, 
        scope=Scope.user_info, 
        help="The user's best time for the matching game."
    )
    #need field for selected containers - probably a dictionary of two indices referring to the list field's values
    #if the dictionary of indices doesn't work, two separate fields is also viable
    #may need field for page number if list_length field is not enough
    #field for current time likely necessary, will need ot look up how to use it in real-time

    #Following fields for editor only--------------------------------------------------------------
    shuffle = Boolean(
        default=True, 
        scope=Scope.settings, 
        help="Whether to shuffle or not. For flashcards only?"
    )
    timer = Boolean(
        default=True, 
        scope=Scope.settings, 
        help="Whether to enable the timer for the matching game."
    )

    #Important functions (unmodified)--------------------------------------------------------------
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
        frag.initialize_js('GamesXBlock')
        return frag
    
    #Universal handlers--------------------------------------------------------------
    @XBlock.json_handler
    def expand_game(self, data, suffix=''):
        """
        A handler to expand the game from its title block.
        """
        description = "ERR: self.type not defined or invalid"
        if self.type == "flashcards":
            description = "Click each card to reveal the definition"
        elif self.type == "matching":
            description = "Match each term with the correct definition"
        return {
            'title': self.title,
            'description': description,
            'type': self.type
        }
    
    @XBlock.json_handler
    def start_game(self, data, suffix=''):
        """
        A handler to begin the game.
        """
        return {
            'term_image': self.list[self.list_index]['term_image'],
            'definition_image': self.list[self.list_index]['definition_image'],
            'term': self.list[self.list_index]['term'],
            'list_length': self.list_length,
        }

    @XBlock.json_handler
    def close_game(self, data, suffix=''):
        """
        A handler to close the game to its title block.
        """
        if self.type == "flashcards":
            self.term_is_visible=True
            self.list_index=0
        return {
            'title': self.title
        }
    
    @XBlock.json_handler
    def display_help(self, data, suffix=''):
        """
        A handler to display a tooltip message above the help icon.
        """
        message = "ERR: self.type not defined or invalid"
        if self.type == "flashcards":
            message = "Click each card to reveal the definition"
        elif self.type == "matching":
            message = "Match each term with the correct definition"
        return {'message': message}

    
    #Flashcards handlers--------------------------------------------------------------    
    @XBlock.json_handler
    def flip_flashcard(self, data, suffix=''):
        """
        A handler to flip the flashcard from term to definition
        and vice versa.
        """

        #flip term_is_visible first to show definition
        self.term_is_visible = not(self.term_is_visible)

        #term_is_visible has already been flipped, so the conditional evaluates the original value by flipping it again
        #When reviewing this logic, pretend that the not() function below is not there since term_is_visible was already flipped once above
        if not(self.term_is_visible):
            return {'image': self.list[self.list_index]['definition_image'], 'text': self.list[self.list_index]['definition']}
        return {'image': self.list[self.list_index]['term_image'], 'text': self.list[self.list_index]['term']}

    @XBlock.json_handler
    def page_turn(self, data, suffix=''):
        """
        A handler to turn the page to a new flashcard (left or right) in the list.
        """
        #Always display the term first for a new flashcard.
        self.term_is_visible = True

        if data['nextIndex'] == 'left':
            if self.list_index>0:
                self.list_index-=1
            #if the current index is 0, circulate to the last flashcard
            else:
                self.list_index=len(self.list)-1
            return {'term_image': self.list[self.list_index]['term_image'], 'term': self.list[self.list_index]['term'], 'index': self.list_index+1, 'list_length': self.list_length}

        #data['nextIndex'] == 'right' here
        if self.list_index<len(self.list)-1:
            self.list_index+=1
        #if the current index is the last flashcard, circulate to the first flashcard
        else:
            self.list_index = 0
        return {'term_image': self.list[self.list_index]['term_image'], 'term': self.list[self.list_index]['term'], 'index': self.list_index+1, 'list_length': self.list_length}
    
    #Matching handlers--------------------------------------------------------------
    @XBlock.json_handler
    def select_container(self, data, suffix=''):
        #this function will require a lot of logic:
            #1. if no other container is selected, allow selection to proceed
            #2. if another container is already selected:
                #a. but it is the same type as the container the user is currently trying to select (i.e. 'term') it is not a match
                #b. and the current container is the other type (i.e. 'term' and 'def') check to see if the term and definition are a match
            #3. if the container in question is the container that is already selected, deselect it
        return {}
        
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Multiple GamesXBlock",
             """<vertical_demo>
                <games/>
                <games/>
                <games/>
                </vertical_demo>
             """),
             ("gamesblock",
              """<games/>
              """)
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

    '''
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
        '''
    #)