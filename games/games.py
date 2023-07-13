"""An XBlock providing gamification capabilities."""
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock

#May need to import more or less field types later (https://github.com/openedx/XBlock/blob/master/xblock/fields.py)
from xblock.fields import Integer, Scope, String, Boolean, List, Dict

#need these libraries for random string generation
import string
import random

class GamesXBlock(XBlock):
    """
    An XBlock for creating games.

    The Student view will display the game content and allow the student to interact
    accordingly.

    The editor view will allow course authors to create and manipulate the games.
    """

    #Universal fields------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    title = String(
        default="Matching", 
        scope=Scope.content, 
        help="The title of the block to be displayed in the xblock."
    )

    #Change default to 'matching' for matching game and 'flashcards' for flashcards game to test
    type = String(
        default="matching", 
        scope=Scope.settings, 
        help="The kind of game this xblock is responsible for ('flashcards' or 'matching' for now)."
    )

    #Matching and flashcards will use the same list, but term_image and definition_image will only be used in flashcards
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
            }
        ],
        scope=Scope.content,
        help="The list of terms and definitions."
    )

    list_length = Integer(
        default=len(list.default),
        scope=Scope.content,
        help="A field for the length of the list for convenience."
    )

    #Flashcard game fields------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

    #Matching game fields------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    best_time = Integer(
        default=None, 
        scope=Scope.user_info, 
        help="The user's best time for the matching game."
    )

    game_started = Boolean(
        default = False,
        scope=Scope.settings,
        help="Bool variable to allow the timer to start from 0 after the game starts."
    )

    time_seconds = Integer(
        default=0,
        scope=Scope.user_info,
        help="The current time elapsed in seconds since starting the matching game."
    )

    selected_containers = Dict(
        default={},
        scope=Scope.settings,
        help="A dictionary to keep track of selected containers for the matching game."
    )

    matching_id_list = List(
        default=[],
        scope=Scope.settings,
        help="A list of all the matching game ids."
    )

    matching_id_dictionary_index = Dict(
        default={},
        scope=Scope.settings,
        help="A dictionary to encrypt the ids of the terms and definitions for the matching game."
    )

    matching_id_dictionary_type = Dict(
        default={},
        scope=Scope.settings,
        help="A dictionary to tie the id to the type of container (term or definition) for the matching game."
    )

    matching_id_dictionary = Dict(
        default={},
        scope=Scope.settings,
        help="A dictionary to encrypt the ids of the terms and definitions for the matching game."
    )

    match_count = Integer(
        default=0,
        scope=Scope.settings,
        help="Tracks how many matches have been successfully made. Used to determine when to switch pages."
    )

    matches_remaining = Integer(
        default = len(list.default),
        scope=Scope.content,
        help = "The number of matches that remain in the list."
    )

    '''
    #Following fields for editor only------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
    '''

    #Important functions (unmodified from xblock installation)------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
        #frag.initialize_js('FlashcardsXBlock')
        return frag
    
    #Universal handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
    def close_game(self, data, suffix=''):
        """
        A handler to close the game to its title block.
        """

        self.game_started = False
        self.time_seconds = 0
        self.match_count = 0
        self.matches_remaining = self.list_length

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

    #Flashcards handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------    
    @XBlock.json_handler
    def start_game_flashcards(self, data, suffix=''):
        """
        A handler to begin the flashcards game.
        """
        return {            
            'list': self.list,
            'list_index': self.list_index,
            'list_length': self.list_length
        }
    
    @XBlock.json_handler
    def flip_flashcard(self, data, suffix=''):
        """
        A handler to flip the flashcard from term to definition
        and vice versa.
        """
        if self.term_is_visible:
            self.term_is_visible = not(self.term_is_visible)
            return {'image': self.list[self.list_index]['definition_image'], 'text': self.list[self.list_index]['definition']}
        
        self.term_is_visible = not(self.term_is_visible)
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
            #else if the current index is 0, circulate to the last flashcard
            else:
                self.list_index=len(self.list)-1
            return {'term_image': self.list[self.list_index]['term_image'], 'term': self.list[self.list_index]['term'], 'index': self.list_index+1, 'list_length': self.list_length}

        #else data['nextIndex'] == 'right'
        if self.list_index<len(self.list)-1:
            self.list_index+=1
        #else if the current index is the last flashcard, circulate to the first flashcard
        else:
            self.list_index = 0
        return {'term_image': self.list[self.list_index]['term_image'], 'term': self.list[self.list_index]['term'], 'index': self.list_index+1, 'list_length': self.list_length}
    
    #Matching handlers------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    @XBlock.json_handler
    def start_game_matching(self, data, suffix=''):
        """
        A handler to begin the matching game.
        """
        #function to return a random ascii string of 6 characters (upper- and lower-case)
        def randomString():
            return str(''.join(random.choices(string.ascii_letters, k=6)))

        #set game fields accordingly
        self.game_started = True
        self.time_seconds = 0
        self.selected_containers = {}
        self.match_count = 0
        self.matches_remaining = self.list_length

        #create dictionaries and key-value pairs to reference the list based on ids that will be sent to games.js
        for i in range(0, 2*self.list_length, 2):
            #the ids are random strings stored into an indexed list
            uniqueString = randomString()
            while uniqueString in self.matching_id_list:
                uniqueString = randomString()
            self.matching_id_list.append(uniqueString) #append id at index i

            while uniqueString in self.matching_id_list:
                uniqueString = randomString()
            self.matching_id_list.append(uniqueString) #append id at index i+1

            #the random string ids are the dictionary keys for the indices, types, and container content that they reference in the list
            self.matching_id_dictionary_index[self.matching_id_list[i]] = i//2
            self.matching_id_dictionary_index[self.matching_id_list[i+1]] = i//2

            self.matching_id_dictionary_type[self.matching_id_list[i]] = "term"
            self.matching_id_dictionary_type[self.matching_id_list[i+1]] = "definition"

            self.matching_id_dictionary[self.matching_id_list[i]] = self.list[i//2]['term']
            self.matching_id_dictionary[self.matching_id_list[i+1]] = self.list[i//2]['definition']

        return {            
            'list': self.list,
            'list_index': self.list_index,
            'list_length': self.list_length,
            'id_dictionary_index': self.matching_id_dictionary_index,
            'id_dictionary': self.matching_id_dictionary,
            'id_list': self.matching_id_list,
            'time': "0:00"
        }
    
    @XBlock.json_handler
    def update_timer(self, data, suffix=''):
        """
        A handler to update the timer. This is called every 1000ms by an ajax call in games.js.
        """

        #only increment the timer if the game has started
        if self.game_started:
            self.time_seconds += 1

        return {'value': self.time_seconds, 'game_started': self.game_started}
        
    @XBlock.json_handler
    def select_container(self, data, suffix=''):
        """
        A handler for selecting matching game containers and evaluating matches.
        """

        #add a '#' to id for use with jQuery (this could be done in the js file as well)
        id = "#"+data['id']
        container_type = self.matching_id_dictionary_type[data['id']]
        index = self.matching_id_dictionary_index[data['id']]

        #if no container is selected yet
        if len(self.selected_containers) == 0:
            self.selected_containers['container1_id'] = id
            self.selected_containers['container1_type'] = container_type
            self.selected_containers['container1_index'] = index
            return {'first_selection': True, 'deselect': False, 'id': id, 'prev_id': None, 'match': False, 'match_count': self.match_count, 'matches_remaining': self.matches_remaining, 'list': self.list, 'list_length': self.list_length, 'id_list': self.matching_id_list, 'id_dictionary': self.matching_id_dictionary, 'time_seconds': self.time_seconds}
        
        #else

        #establish prev_id before conditionals since the selected_containers dictionary is cleared before returning to js
        prev_id = self.selected_containers['container1_id']

        #if the container referenced by 'id' is already selected, deselect it
        if id == self.selected_containers['container1_id']:
            self.selected_containers.clear()
            return {'first_selection': False, 'deselect': True, 'id': id, 'prev_id': prev_id, 'match': False, 'match_count': self.match_count, 'matches_remaining': self.matches_remaining, 'list': self.list, 'list_length': self.list_length, 'id_list': self.matching_id_list, 'id_dictionary': self.matching_id_dictionary, 'time_seconds': self.time_seconds}
        
        #containers with the same type cannot match (i.e. a term with a term, etc.)
        if container_type == self.selected_containers['container1_type']:
            self.selected_containers.clear()
            return {'first_selection': False, 'deselect': False, 'id': id, 'prev_id': prev_id, 'match': False, 'match_count': self.match_count, 'matches_remaining': self.matches_remaining, 'list': self.list, 'list_length': self.list_length, 'id_list': self.matching_id_list, 'id_dictionary': self.matching_id_dictionary, 'time_seconds': self.time_seconds}
    
        #if the execution gets to this point and the indices are the same, this implies a term/ definition match
        if index == self.selected_containers['container1_index']:
            self.selected_containers.clear()
            self.match_count += 1
            self.matches_remaining -= 1
            return {'first_selection': False, 'deselect': False, 'id': id, 'prev_id': prev_id, 'match': True, 'match_count': self.match_count, 'matches_remaining': self.matches_remaining, 'list': self.list, 'list_length': self.list_length, 'id_list': self.matching_id_list, 'id_dictionary': self.matching_id_dictionary, 'time_seconds': self.time_seconds}
        
        #not a match
        self.selected_containers.clear()
        return {'first_selection': False, 'deselect': False, 'id': id, 'prev_id': prev_id, 'match': False, 'match_count': self.match_count, 'matches_remaining': self.matches_remaining, 'list': self.list, 'list_length': self.list_length, 'id_list': self.matching_id_list, 'id_dictionary': self.matching_id_dictionary, 'time_seconds': self.time_seconds}
        
    @XBlock.json_handler
    def end_game_matching(self, data, suffix=''):
        """
        A handler to end the matching game and compare the user's time to the best_time field.
        """
        self.game_started = False
        self.time_seconds = 0
        self.selected_containers = {}
        self.match_count = 0
        self.matches_remaining = self.list_length

        new_time = data['newTime']
        prev_time = self.best_time
        new_record = False
        first_attempt = False

        #update record if it is beaten, need to check if best time is null before comparing it since we can't compare null and int
        if self.best_time is None:
            first_attempt = True
            new_record = True
            self.best_time = new_time
            return {'new_time': new_time, 'prev_time': prev_time, 'new_record': new_record, 'first_attempt': first_attempt}
        
        if new_time < self.best_time:
            new_record = True
            self.best_time = new_time

        return {'new_time': new_time, 'prev_time': prev_time, 'new_record': new_record, 'first_attempt': first_attempt}

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
             ("games",
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