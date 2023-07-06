/* Javascript for GamesXBlock. */

function GamesXBlock(runtime, element) {
    //Universal functions--------------------------------------------------------------
    //Function to expand the game from its title block
    function expandGame(fullView) {
        $('.title-initial', element).remove();

        var expandedBlock = "<div class='background-block'></div>";
        var topDiv = "<div class='flashcard-top'></div>";
        var title = "<div class='title-persistent'></div>";
        var closeButton = "<div class='close-button'></div>";
        var closeBackground = "<div class='close-background'></div>";
        var closeImage = "<svg class='close-image' xmlns='http://www.w3.org/2000/svg' width='24' height='25' viewBox='0 0 24 25' fill='none'><path d='M19 6.71078L17.59 5.30078L12 10.8908L6.41 5.30078L5 6.71078L10.59 12.3008L5 17.8908L6.41 19.3008L12 13.7108L17.59 19.3008L19 17.8908L13.41 12.3008L19 6.71078Z' fill='#707070'/></svg>"
        var startBlock = "<div class='start-block'></div>";
        var description = "<div class='flashcard-description'></div>";

        switch(fullView.type){
            case 'flashcards': var startButton = "<div class='start-button-flashcards'>Start</div>"; break;
            case 'matching': var startButton = "<div class='start-button-matching'>Start</div>"; break;
            default: var startButton = "<div>ERR: invalid type</div>";
        }

        $('.gamesxblock', element).append(expandedBlock);
        $('.background-block', element).append(topDiv);
        $('.flashcard-top', element).append(title);
        $('.title-persistent', element).text(fullView.title);
        $('.flashcard-top', element).append(closeButton);
        $('.close-button', element).append(closeBackground);
        $('.close-background', element).append(closeImage);
        $('.background-block', element).append(startBlock);
        $('.start-block', element).append(description);
        $('.flashcard-description', element).text(fullView.description);
        $('.start-block', element).append(startButton);
    }

    $(document).on('click', '.title-initial', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'expand_game'),
            data: JSON.stringify({}),
            success: expandGame
        });
    });

    //Function to close the current game back to the title block
    function closeGame(initialView) {
        var init = "<div class='title-initial'></div>";

        $('.background-block', element).remove();
        $('.gamesxblock', element).append(init);
        $('.title-initial', element).text(initialView.title);
    }

    $(document).on('click', '.close-image', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'close_game'),
            data: JSON.stringify({}),
            success: closeGame
        });
    })

    //Function to show and hide the game's tooltip
    function getHelp(help) {
        var tooltip = "<div class='tooltip'></div>";
        var tooltipText = "<div class='tooltip-text'></div>";

        $('.help-outline', element).append(tooltip);
        $('.tooltip', element).append(tooltipText);
        $('.tooltip-text', element).text(help.message);
    }

    function hideHelp(help) {
        $('.tooltip', element).remove();
    }

    $(document).on('mouseenter', '.help', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'display_help'),
            data: JSON.stringify({}),
            success: getHelp
        });
    });

    $(document).on('mouseleave', '.help', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'display_help'),
            data: JSON.stringify({}),
            success: hideHelp
        });
    });

    //Flashcards functions--------------------------------------------------------------
    //Function to start the flashcards game
    function startFlashcards(firstCard) {
        $('.start-block', element).remove();

        var flashcardBlock = "<div class='flashcard-block'></div>";
        var firstImage = "<image class='image'>";
        var text = "<div class='flashcard-text'></div>";
        var footer = "<div class='flashcard-footer'></div>";
        var spacer = "<div class='spacer'></div>";
        var help = "<div class='help'></div>";
        var helpOutline = "<div class='help-outline'><svg xmlns='http://www.w3.org/2000/svg' width='24' height='25' viewBox='0 0 24 25' fill='none'><g clip-path='url(#clip0_7867_247475)'><path d='M11 18.3008H13V16.3008H11V18.3008ZM12 2.30078C6.48 2.30078 2 6.78078 2 12.3008C2 17.8208 6.48 22.3008 12 22.3008C17.52 22.3008 22 17.8208 22 12.3008C22 6.78078 17.52 2.30078 12 2.30078ZM12 20.3008C7.59 20.3008 4 16.7108 4 12.3008C4 7.89078 7.59 4.30078 12 4.30078C16.41 4.30078 20 7.89078 20 12.3008C20 16.7108 16.41 20.3008 12 20.3008ZM12 6.30078C9.79 6.30078 8 8.09078 8 10.3008H10C10 9.20078 10.9 8.30078 12 8.30078C13.1 8.30078 14 9.20078 14 10.3008C14 12.3008 11 12.0508 11 15.3008H13C13 13.0508 16 12.8008 16 10.3008C16 8.09078 14.21 6.30078 12 6.30078Z' fill='#00262B'/></g><defs><clipPath id='clip0_7867_247475'><rect width='24' height='24' fill='white' transform='translate(0 0.300781)'/></clipPath></defs></svg></div>";
        var navigation = "<div class='flashcard-navigation'></div>";
        var left = "<div class='flashcard-left-button'></div>";
        var leftImage = "<svg class='flashcard-left-image' xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill='none'><g clip-path='url(#clip0_7867_247470)'><path d='M14.4796 18.3008L15.8896 16.8908L11.3096 12.3008L15.8896 7.71078L14.4796 6.30078L8.47965 12.3008L14.4796 18.3008Z' fill='#00262B'/></g><defs><clipPath id='clip0_7867_247470'><rect width='24' height='24' fill='white' transform='translate(24.5 24.3008) rotate(-180)'/></clipPath></defs></svg>";
        var navText = "<div class='flashcard-navigation-text'></div>";
        var right = "<div class='flashcard-right-button'></div>";
        var rightImage = "<svg class='flashcard-right-image' xmlns='http://www.w3.org/2000/svg' width='25' height='25' viewBox='0 0 25 25' fill='none'><g clip-path='url(#clip0_7867_247473)'><path d='M10.5204 6.30078L9.11035 7.71078L13.6904 12.3008L9.11035 16.8908L10.5204 18.3008L16.5204 12.3008L10.5204 6.30078Z' fill='#00262B'/></g><defs><clipPath id='clip0_7867_247473'><rect width='24' height='24' fill='white' transform='translate(0.5 0.300781)'/></clipPath></defs></svg>";

        $('.background-block', element).append(flashcardBlock);
        $('.flashcard-block', element).append(firstImage);
        $('.image', element).attr("src", firstCard.term_image);
        $('.flashcard-block', element).append(text);
        $('.flashcard-text', element).text(firstCard.term);
        $('.background-block', element).append(footer);
        $('.flashcard-footer', element).append(spacer);
        $('.flashcard-footer', element).append(navigation);
        $('.flashcard-footer', element).append(help);
        $('.help', element).append(helpOutline);
        $('.flashcard-navigation', element).append(left);
        $('.flashcard-left-button', element).append(leftImage);
        $('.flashcard-navigation', element).append(navText);
        $('.flashcard-navigation-text', element).text("1" + " / " + firstCard.list_length);
        $('.flashcard-navigation', element).append(right);
        $('.flashcard-right-button', element).append(rightImage);
    }

    $(document).on('click', '.start-button-flashcards', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'start_game'),
            data: JSON.stringify({}),
            success: startFlashcards
        });
    });

    //Function to flip the current flashcard
    function flipFlashcard(newSide) {
        $('.image', element).attr("src", newSide.image);
        $('.flashcard-text', element).text(newSide.text);
    }

    $(document).on('click', '.flashcard-block', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'flip_flashcard'),
            data: JSON.stringify({}),
            success: flipFlashcard
        });
    });

    //Function to turn the page to another flashcard
    function pageTurn(nextCard) {
        $('.image', element).attr("src", nextCard.term_image);
        $('.flashcard-text', element).text(nextCard.term);
        $('.flashcard-navigation-text', element).text(nextCard.index + " / " + nextCard.list_length);
    }

    $(document).on('click', '.flashcard-left-button', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'page_turn'),
            data: JSON.stringify({nextIndex: 'left'}),
            success: pageTurn
        });
    });

    $(document).on('click', '.flashcard-right-button', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'page_turn'),
            data: JSON.stringify({nextIndex: 'right'}),
            success: pageTurn
        });
    });

    //Matching functions--------------------------------------------------------------
    //Function to start the matching game
    function startMatching(firstPage) {
        $('.start-block', element).remove();
    }

    $(document).on('click', '.start-button-matching', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'start_game'),
            data: JSON.stringify({}),
            success: startMatching
        });
    });
    /*
    //Function to select a container displaying either a term or a definition
    function selectContainer(selected) {

    }

    $(document).on('', '', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, ''),
            data: JSON.stringify({}),
            success: selectContainer
        });
    });
    */

    return {};

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}







//Old stuff - no longer has a purpose. Will delete once editor view is complete.
/*
    //////////////////////////////////////////////////////////////
    //Timer Flip
    function flipTimer(newTimer) {
        $('.timer_bool .timer_flip', element).text(newTimer.timer);
    }

    $('.timer_bool', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'flip_timer'),
            data: JSON.stringify({}),
            success: flipTimer
        });
    });
    //////////////////////////////////////////////////////////////

    //////////////////////////////////////////////////////////////
    //Shuffle Flip
    function flipShuffle(newShuffle) {
        $('.shuffle_bool .shuffle_flip', element).text(newShuffle.shuffle);
    }

    $('.shuffle_bool', element).click(function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'flip_shuffle'),
            data: JSON.stringify({}),
            success: flipShuffle
        });
    });
    //////////////////////////////////////////////////////////////
*/