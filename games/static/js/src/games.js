/* Javascript for GamesXBlock. */

function GamesXBlock(runtime, element) {
    //Universal functions------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    //Expand Game
    function expandGame(fullView) {
        //Function to expand the game from its title block

        $('.title-initial', element).remove();

        var expandedBlock = "<div class='background-block'></div>";
        var topDiv = "<div class='game-top'></div>";
        var title = "<div class='title-persistent'></div>";
        var closeButton = "<div class='close-button'></div>";
        var closeBackground = "<div class='close-background'></div>";
        var closeImage = "<svg class='close-image' xmlns='http://www.w3.org/2000/svg' width='24' height='25' viewBox='0 0 24 25' fill='none'><path d='M19 6.71078L17.59 5.30078L12 10.8908L6.41 5.30078L5 6.71078L10.59 12.3008L5 17.8908L6.41 19.3008L12 13.7108L17.59 19.3008L19 17.8908L13.41 12.3008L19 6.71078Z' fill='#707070'/></svg>"
        var startBlock = "<div class='start-block'></div>";
        var description = "<div class='game-description'></div>";

        //Depending on the game type, add the respective start button; add new cases for new game types
        switch(fullView.type){
            case 'flashcards': var startButton = "<div class='start-button-flashcards'>Start</div>"; break;
            case 'matching': var startButton = "<div class='start-button-matching'>Start</div>"; break;
            default: var startButton = "<div>ERR: invalid type</div>";
        }

        $('.gamesxblock', element).append(expandedBlock);
        $('.background-block', element).append(topDiv);
        $('.game-top', element).append(title);
        $('.title-persistent', element).text(fullView.title);
        $('.game-top', element).append(closeButton);
        $('.close-button', element).append(closeBackground);
        $('.close-background', element).append(closeImage);
        $('.background-block', element).append(startBlock);
        $('.start-block', element).append(description);
        $('.game-description', element).text(fullView.description);
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

    //Close Game
    function closeGame(initialView) {
        //Function to close the current game back to the title block

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

    //Help
    function getHelp(help) {
        //Function to show the game's tooltip

        var tooltip = "<div class='tooltip'></div>";
        var tooltipText = "<div class='tooltip-text'></div>";

        $('.help-outline', element).append(tooltip);
        $('.tooltip', element).append(tooltipText);
        $('.tooltip-text', element).text(help.message);
    }
    function hideHelp(help) {
        //Function to hide the game's tooltip

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

    //Flashcards functions------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    //Start Flashcards
    function startFlashcards(firstCard) {
        //Function to start the flashcards game

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
        $('.image', element).attr("src", firstCard.list[firstCard.list_index]['term_image']);
        $('.flashcard-block', element).append(text);
        $('.flashcard-text', element).text(firstCard.list[firstCard.list_index]['term']);
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
            url: runtime.handlerUrl(element, 'start_game_flashcards'),
            data: JSON.stringify({}),
            success: startFlashcards
        });
    });

    //Flip Flashcard
    function flipFlashcard(newSide) {
        //Function to flip the current flashcard

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

    //Turn Page
    function pageTurn(nextCard) {
        //Function to turn the page to another flashcard

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

    //Matching functions------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    //Start Matching
    function startMatching(firstPage) {
        //Function to start the matching game

        $('.start-block', element).remove();

        //the css style changes made by jquery are not persistent after the element is removed, so the following line does not need to be undone when closeGame is called
        $('.background-block', element).css({"height":"initial", "padding":"20px 24px 24px 24px"});

        var matchingBlock = "<div class='matching-block'></div>";
        var matchingColumnL = "<div class='matching-column-l'></div>"
        var matchingColumnR = "<div class='matching-column-r'></div>";

        $('.background-block', element).append(matchingBlock);
        $('.matching-block', element).append(matchingColumnL);
        $('.matching-block', element).append(matchingColumnR);

        //progress shown by default, but if there are 5 or less pairs, it will not be displayed
        var showProgress = true;

        //add the first five items to the left column
        for (let i=0; i<5; i++) {
            //if there are no more terms to add, use empty containers instead to account for formatting
            if (i>2*firstPage.list_length-1) {
                showProgress = false;
                var emptyContainer = "<div class='matching-container-empty'></div>";
                $('.matching-column-l', element).append(emptyContainer);
                continue;
            }
            var id = firstPage.id_list[i];
            var content = firstPage.id_dictionary[id]
            var container = "<div class='matching-container' id=" + id + ">" + content + "</div>";
            $('.matching-column-l', element).append(container);
        }
        //add the next five items to the right column
        for (let i=5; i<10; i++) {
            //if there are no more terms to add, use empty containers instead to account for formatting
            if (i>2*firstPage.list_length-1) {
                showProgress = false;
                var emptyContainer = "<div class='matching-container-empty'></div>";
                $('.matching-column-r', element).append(emptyContainer);
                continue;
            }
            var id = firstPage.id_list[i];
            var content = firstPage.id_dictionary[id]
            var container = "<div class='matching-container' id=" + id + ">" + content + "</div>";
            $('.matching-column-r', element).append(container);
        }

        var footer = "<div class='matching-footer'></div>";
        var progressContainer = "<div class='matching-progress-container'></div>";
        var progressIndicator = "<div class='matching-progress-indicator'></div>";
        var progressText = "<div class='matching-progress-text'></div>";
        var timer = "<div class='matching-timer'>" + firstPage.time + "</div>";
        var help = "<div class='help'></div>";
        var helpOutline = "<div class='help-outline'><svg xmlns='http://www.w3.org/2000/svg' width='24' height='25' viewBox='0 0 24 25' fill='none'><g clip-path='url(#clip0_7867_247475)'><path d='M11 18.3008H13V16.3008H11V18.3008ZM12 2.30078C6.48 2.30078 2 6.78078 2 12.3008C2 17.8208 6.48 22.3008 12 22.3008C17.52 22.3008 22 17.8208 22 12.3008C22 6.78078 17.52 2.30078 12 2.30078ZM12 20.3008C7.59 20.3008 4 16.7108 4 12.3008C4 7.89078 7.59 4.30078 12 4.30078C16.41 4.30078 20 7.89078 20 12.3008C20 16.7108 16.41 20.3008 12 20.3008ZM12 6.30078C9.79 6.30078 8 8.09078 8 10.3008H10C10 9.20078 10.9 8.30078 12 8.30078C13.1 8.30078 14 9.20078 14 10.3008C14 12.3008 11 12.0508 11 15.3008H13C13 13.0508 16 12.8008 16 10.3008C16 8.09078 14.21 6.30078 12 6.30078Z' fill='#00262B'/></g><defs><clipPath id='clip0_7867_247475'><rect width='24' height='24' fill='white' transform='translate(0 0.300781)'/></clipPath></defs></svg></div>";

        $('.background-block', element).append(footer);
        //add progress container regardless for formatting
        $('.matching-footer', element).append(progressContainer);
        if(showProgress) {
            var pageCount = Math.floor((firstPage.list_length-1)/5)+1;
            var currentProgressDeg = 360*(1/pageCount);
            var progressIndicatorStyle = "conic-gradient(#0d7d4d " + currentProgressDeg + "deg, #f2f0ef 0deg";
            $('.matching-progress-container', element).append(progressIndicator);
            $('.matching-progress-indicator', element).append(progressText);
            $('.matching-progress-indicator', element).css("background", progressIndicatorStyle)
            $('.matching-progress-text', element).text("1 " + "/" + " " + pageCount);
        }
        $('.matching-footer', element).append(timer);
        $('.matching-footer', element).append(help);
        $('.help', element).append(helpOutline);
    }
    $(document).on('click', '.start-button-matching', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'start_game_matching'),
            data: JSON.stringify({}),
            success: startMatching
        });
    });

    //Timer
    function formatTime(timeSeconds) {
        //Function to format the time_seconds field (for use by other functions)

        var seconds = ":" + timeSeconds%60;
        if (timeSeconds%60 < 10) 
            var seconds = ":0" + timeSeconds%60;

        var minutes = Math.floor(timeSeconds/60)%60;

        var hours = "";
        if (timeSeconds >= 3600) {
            var hours = Math.floor(timeSeconds/3600)%24 + ":";
            if (Math.floor(timeSeconds/60)%60 < 10)
                hours = Math.floor(timeSeconds/3600)%24 + ":0";
        }

        //returns as a string formatted as (HH:M)M:SS, where (HH:M) only appear if they are relevant
        return hours + minutes + seconds;
    }
    function updateTimer(newTime) {
        //Function to update the timer

        //do nothing until the game starts
        if (!newTime.game_started)
            return;
        $('.matching-timer', element).text(formatTime(newTime.value));
    }
    $(document).ready(function() {
        //Update the timer every 1000 ms
        setInterval(function() {
            $.ajax({
                type: "POST",
                url: runtime.handlerUrl(element, 'update_timer'),
                data: JSON.stringify({}),
                cache: false,
                success: updateTimer
            });
        }, 1000);
    });

    //Select Container
    function selectContainer(selected) {
        //Function to handle selecting containers displaying either a term or a definition (also covers matches and deselcting)

        //first selection; when no other container is selected, select the container that was clicked
        if (selected.first_selection) {
            //cancel all animations if another container is selected in case they are not finished yet
            $('.matching-container', element).css("animation-name", "initial");

            $('.matching-container', element).css("border", "2px solid var(--light-300, #F2F0EF)");
            $('.matching-container', element).css("background-color", "initial");
            $(selected.id).css("border", "2px solid var(--primary-500, #00262B)");
            return;
        }

        //deselect; when a selected container is selected again, deselect it
        if (selected.deselect) {
            $(selected.id).css("border", "2px solid var(--light-300, #F2F0EF)");
            $(selected.id).css("background-color", "initial");
            return;
        }

        //false match; if the second container selected does not match the first container, run the 'incorrect' animation on the two selected then deselect them
        if (!selected.match) {
            //reset the previously selected element's border before the animation so that it does not appear selected after the animation
            $(selected.prev_id).css("border", "2px solid var(--light-300, #F2F0EF)");

            $(selected.id).css({"animation-name": "incorrect"});
            $(selected.prev_id).css({"animation-name": "incorrect"});

            //if the animation-name is not reset in the 'first selection' section above, the animations will only be able to fire once
            return;
        }

        //match; if the second container selected matches the first container, change their classes to 'matching-container-empty' and run the 'correct' animation
        //reset the borders to white to prevent the dark border to persist
        $(selected.id).css("border", "2px solid #ffffff");
        $(selected.prev_id).css("border", "2px solid #ffffff");
        //replace the class and apply the correct animation
        $(selected.id).removeClass("matching-container");
        $(selected.prev_id).removeClass("matching-container");
        $(selected.id).addClass("matching-container-empty");
        $(selected.prev_id).addClass("matching-container-empty");
        $(selected.id).css({"animation-name": "correct"});
        $(selected.prev_id).css({"animation-name": "correct"});

        //next page; every 5 matches, display the next 5 pairs or whatever remains
        if (selected.match_count%5 == 0 && selected.matches_remaining > 0) {
            //clear the page
            for(let i=2*selected.match_count-10; i<2*selected.match_count; i++) {
                id = "#" + selected.id_list[i];
                $(id).remove();
            }
            //add the next 5 items to the left column
            for (let i=2*selected.match_count; i<2*selected.match_count+5; i++) {
                //if there are no more terms to add, use empty containers instead to account for formatting
                if (i>2*selected.list_length-1) {
                    var emptyContainer = "<div class='matching-container-empty'></div>";
                    $('.matching-column-l', element).append(emptyContainer);
                    continue;
                }
                var id = selected.id_list[i];
                var content = selected.id_dictionary[id]
                var container = "<div class='matching-container' id=" + id + ">" + content + "</div>";
                $('.matching-column-l', element).append(container);
            }
            //add the next 5 items to the right column
            for (let i=2*selected.match_count+5; i<2*selected.match_count+10; i++) {
                //if there are no more terms to add, use empty containers instead to account for formatting
                if (i>2*selected.list_length-1) {
                    var emptyContainer = "<div class='matching-container-empty'></div>";
                    $('.matching-column-r', element).append(emptyContainer);
                    continue;
                }
                var id = selected.id_list[i];
                var content = selected.id_dictionary[id]
                var container = "<div class='matching-container' id=" + id + ">" + content + "</div>";
                $('.matching-column-r', element).append(container);
            }

            //if the progress indicator exists, it will be updated, otherwise this will simply have no effect
            var currentProgress = Math.floor(selected.match_count/5+1);
            var pageCount = Math.floor((selected.list_length-1)/5)+1
            var currentProgressDeg = 360*(currentProgress/pageCount);
            var progressIndicatorStyle = "conic-gradient(#0d7d4d " + currentProgressDeg + "deg, #f2f0ef 0deg";
            $('.matching-progress-indicator', element).css("background", progressIndicatorStyle)
            $('.matching-progress-text', element).text(currentProgress + " " + "/" + " " + pageCount);
        }

        //end game; after the last match is made, end the game with an ajax call
        if (selected.matches_remaining == 0) {
            $.ajax({
                type: "POST",
                url: runtime.handlerUrl(element, 'end_game_matching'),
                data: JSON.stringify({newTime: selected.time_seconds}),
                success: endGameMatching
            });
        }
    }

    //End Matching Game
    function endGameMatching(lastPage) {
        //function for ajax to end matching game

        //changes made regardless (new record or not)
        $('.matching-block', element).remove();
        $('.matching-footer', element).remove();

        var endBlock = "<div class='matching-end-block'></div>";
        var endFooter = "<div class='matching-footer'></div>";

        $('.background-block', element).append(endBlock);
        $('.background-block', element).append(endFooter);
        $('.matching-footer', element).css("height", "48px");

        //new record; Show confetti and new best
        if (lastPage.new_record) {
            var textBlock = "<div class='matching-record-text-block'></div>";
            var congrats = "<div class='matching-end-congratulations'>Congratulations!</div>";
            var newTime = "<div class='matching-end-record-time'>" + formatTime(lastPage.new_time) + "</div>";
            var message = "<div class='matching-end-record-message'>A new personal best!</div>";
            //only display previous time if it exists
            if (lastPage.prev_time != null) {
                var previousBlock = "<div class='matching-end-record-previous-block'></div>";
                var previousText = "<div class='matching-end-record-previous-text'>Previous best:</div>";
                var previousTime = "<div class='matching-end-record-previous-time'>" + formatTime(lastPage.prev_time) + "</div>";
            }
            var replayButton = "<div class='matching-replay-button'>Play again</div>";

            $('.matching-end-block', element).append(textBlock);
            $('.matching-record-text-block', element).append(congrats);
            $('.matching-record-text-block', element).append(newTime);
            $('.matching-record-text-block', element).append(message);
            //only display previous time if it exists
            if (lastPage.prev_time != null) {
                $('.matching-record-text-block', element).append(previousBlock);
                $('.matching-end-record-previous-block', element).append(previousText);
                $('.matching-end-record-previous-block', element).append(previousTime);
            }
            $('.matching-record-text-block', element).append(replayButton);

            //add 80 confetti particles between 10% and 90% left values on the screen
            for (let i=10; i<=90/*5*Math.floor(Math.random())+25*/; i++) {
                let type = Math.floor(9*Math.random());
                let left = i;
                let duration = 2*Math.random()+1.5;
                switch(type) {
                    case 0: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='15' height='16' viewBox='0 0 15 16' fill='none'><path d='M4.3689 1.70102L4.20772 5.87694L0.634194 8.15426C0.52103 8.22609 0.430148 8.3277 0.3718 8.44764C0.313451 8.56757 0.289954 8.70105 0.303958 8.83303C0.317963 8.96502 0.368912 9.09025 0.45106 9.19462C0.533208 9.29899 0.643286 9.37834 0.768888 9.42372L4.7254 10.8438L5.76617 14.8831C5.7996 15.0112 5.86844 15.1273 5.96496 15.2183C6.06148 15.3093 6.18187 15.3717 6.3126 15.3984C6.44334 15.4252 6.57925 15.4152 6.70507 15.3697C6.8309 15.3241 6.94167 15.2448 7.02493 15.1406L9.63538 11.8407L13.8405 12.0823C13.9741 12.0908 14.1077 12.0619 14.2261 11.9988C14.3444 11.9357 14.4426 11.841 14.5095 11.7255C14.5765 11.61 14.6094 11.4784 14.6046 11.3457C14.5997 11.2131 14.5573 11.0847 14.4822 10.9752L12.1663 7.48355L13.7259 3.59318C13.776 3.46986 13.7903 3.3353 13.767 3.20484C13.7437 3.07439 13.6839 2.95328 13.5943 2.85534C13.5048 2.75739 13.3891 2.68655 13.2604 2.65089C13.1318 2.61523 12.9954 2.61619 12.8668 2.65366L8.80774 3.81192L5.56113 1.14907C5.45667 1.05926 5.32801 1.00149 5.19069 0.982742C5.05337 0.963994 4.91326 0.985062 4.78723 1.04341C4.6612 1.10175 4.55465 1.19488 4.48042 1.31157C4.40619 1.42825 4.36746 1.56351 4.3689 1.70102Z' fill='#F0CC00'/></svg></div>";
                        break;
                    };
                    case 1: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='15' height='15' viewBox='0 0 15 15' fill='none'><path d='M3.74811 1.21691L3.96916 5.20027L0.776141 7.62915C0.674762 7.70687 0.597386 7.81107 0.552749 7.92999C0.508112 8.04891 0.497997 8.17781 0.523546 8.30211C0.549095 8.42642 0.609292 8.54118 0.697332 8.63343C0.785372 8.72568 0.897744 8.79175 1.02176 8.82416L4.91724 9.84429L6.27305 13.5993C6.31641 13.7184 6.39249 13.8231 6.49274 13.9017C6.59299 13.9803 6.71343 14.0297 6.84052 14.0444C6.9676 14.059 7.0963 14.0383 7.21214 13.9846C7.32797 13.9308 7.42635 13.8462 7.49622 13.7402L9.68221 10.3932L13.7103 10.2766C13.8364 10.2689 13.958 10.2269 14.0616 10.1554C14.1652 10.0838 14.2468 9.98545 14.2976 9.87102C14.3483 9.75658 14.3662 9.63053 14.3493 9.5067C14.3323 9.38288 14.2812 9.26605 14.2016 9.16906L11.657 6.07467L12.7917 2.25161C12.8268 2.13003 12.8268 2.0012 12.7919 1.87958C12.757 1.75796 12.6886 1.64836 12.5942 1.56309C12.4998 1.47783 12.3832 1.42027 12.2576 1.39687C12.132 1.37348 12.0022 1.38517 11.8829 1.43065L8.125 2.88798L4.79444 0.638836C4.69035 0.575937 4.57121 0.541547 4.44925 0.539192C4.32729 0.536837 4.2069 0.566601 4.10041 0.625435C3.99392 0.684269 3.90516 0.770055 3.84325 0.873993C3.78135 0.977932 3.74851 1.09628 3.74811 1.21691Z' fill='#D23228'/></svg></div>";
                        break;
                    };
                    case 2: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='11' height='12' viewBox='0 0 11 12' fill='none'><path d='M5.71153 11.2259C8.62645 11.2259 10.9895 8.87555 10.9895 5.97623C10.9895 3.07692 8.62645 0.726562 5.71153 0.726562C2.7966 0.726562 0.433594 3.07692 0.433594 5.97623C0.433594 8.87555 2.7966 11.2259 5.71153 11.2259Z' fill='#F0CC00'/></svg></div>";
                        break;
                    };
                    case 3: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10' fill='none'><path d='M5.03881 9.09091C7.52934 9.09091 9.54831 7.09606 9.54831 4.6353C9.54831 2.17453 7.52934 0.179688 5.03881 0.179688C2.54827 0.179688 0.529297 2.17453 0.529297 4.6353C0.529297 7.09606 2.54827 9.09091 5.03881 9.09091Z' fill='#D23228'/></svg></div>";
                        break;
                    };
                    case 4: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='19' height='20' viewBox='0 0 19 20' fill='none'><path d='M7.02198 0.612796C9.96344 1.66839 12.5617 3.51018 14.5361 5.93919C16.5105 8.36819 17.786 11.2921 18.2247 14.3949L11.161 19.4365C11.161 19.4365 8.60681 9.12353 0.850844 6.98984L7.02198 0.612796Z' fill='#F0CC00'/></svg></div>";
                        break;
                    };
                    case 5: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='19' height='20' viewBox='0 0 19 20' fill='none'><path d='M7.02198 0.612796C9.96344 1.66839 12.5617 3.51018 14.5361 5.93919C16.5105 8.36819 17.786 11.2921 18.2247 14.3949L11.161 19.4365C11.161 19.4365 8.60681 9.12353 0.850844 6.98984L7.02198 0.612796Z' fill='#D23228'/></svg></div>";
                        break;
                    };
                    case 6: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='20' height='14' viewBox='0 0 20 14' fill='none'><path d='M18.6847 12.6267C18.3969 12.824 18.0708 12.9558 17.7358 13.0102C17.4009 13.0646 17.0677 13.0398 16.7665 12.938C11.4582 11.1591 6.57121 8.58468 2.27206 5.30239C1.84252 5.03332 1.49915 4.66316 1.26958 4.22171C1.04 3.78025 0.930651 3.27983 0.950302 2.76071C1.01618 2.18584 1.28373 1.62393 1.7094 1.16646C2.13507 0.708984 2.69381 0.382889 3.29463 0.241256C3.83165 0.0916393 4.38289 0.117982 4.85474 0.315825C5.32658 0.513668 5.68992 0.87081 5.88312 1.32661C6.0696 1.76745 6.05612 2.28317 5.84552 2.76346C9.65696 5.5386 13.9377 7.72986 18.5596 9.27167C18.7989 9.35059 19.0131 9.47608 19.19 9.64093C19.3668 9.80577 19.5028 10.0067 19.5901 10.2322C19.6773 10.4577 19.7142 10.7034 19.6986 10.955C19.683 11.2066 19.6151 11.4592 19.499 11.6984C19.323 12.0675 19.039 12.3913 18.6847 12.6267Z' fill='#DFEAEF'/></svg></div>";
                        break;
                    };
                    case 7: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='33' height='22' viewBox='0 0 33 22' fill='none'><path d='M0.480491 16.2974C0.156876 15.8164 0.0207007 15.2344 0.101927 14.6796C0.183156 14.1248 0.475139 13.6425 0.913626 13.3388C1.35211 13.0352 1.9012 12.9351 2.44009 13.0605C2.97898 13.186 3.46351 13.5267 3.78713 14.0077C4.45967 14.7992 5.27704 15.4428 6.18401 15.8951C7.09098 16.3473 8.06643 16.5977 9.04448 16.6292C9.9686 16.7084 10.8835 16.5768 11.7252 16.2436C12.567 15.9104 13.3154 15.3836 13.9181 14.7L14.0921 14.6006C12.4901 14.2568 10.9392 13.6205 9.51257 12.7217C8.52635 12.1449 7.6448 11.3787 6.91828 10.4668C6.19176 9.55496 5.63452 8.51532 5.27837 7.40727C4.87366 6.08211 4.906 4.68496 5.37005 3.44746C5.8341 2.20995 6.702 1.20639 7.82986 0.603093C8.6534 0.258497 9.55149 0.108944 10.463 0.164596C11.3746 0.220248 12.2782 0.479804 13.1126 0.925615C14.5281 1.66757 15.7828 2.73082 16.7777 4.03161C17.7727 5.3324 18.4808 6.83518 18.8462 8.42161C19.0101 9.10554 19.1202 9.79843 19.1754 10.4931C19.662 10.4161 20.1204 10.33 20.6028 10.2052C23.8768 9.15478 26.9783 7.6622 29.8326 5.76352C30.294 5.50005 30.8504 5.44683 31.3794 5.61557C31.9084 5.78432 32.3667 6.1612 32.6534 6.66331C32.9401 7.16542 33.0317 7.75163 32.9082 8.29298C32.7846 8.83432 32.456 9.28646 31.9946 9.54993C28.8474 11.6588 25.4063 13.2858 21.7671 14.3856C20.7391 14.6566 19.6855 14.8384 18.6169 14.9291C18.266 15.9566 17.7436 16.9003 17.0723 17.719C16.0985 18.8582 14.8804 19.7412 13.5044 20.3057C12.1284 20.8701 10.6281 21.1022 9.10946 20.9854C7.53272 20.9213 5.96288 20.5053 4.50569 19.7653C3.0485 19.0254 1.7378 17.9788 0.6619 16.6959L0.480491 16.2974ZM14.0803 7.22656C13.5073 6.17612 12.633 5.32613 11.5913 4.80679C11.0106 4.45862 10.3377 4.35533 9.7201 4.51957C9.23296 4.79772 8.96573 5.70346 9.18091 6.48435C9.60039 7.61302 10.4067 8.56264 11.4348 9.13881C12.5669 9.83318 13.8034 10.296 15.0732 10.5007C15.0406 10.0684 14.972 9.63718 14.868 9.21198C14.7 8.51975 14.4345 7.8504 14.0803 7.22656Z' fill='#DFEAEF'/></svg></div>";
                        break;
                    };
                    case 8: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='36' height='24' viewBox='0 0 36 24' fill='none'><path d='M1.0001 22.5439C0.92879 22.3673 0.922554 22.1727 0.982737 22.0021C2.34499 18.1282 4.57633 14.7378 7.48867 12.1167C9.65341 10.076 12.315 8.71935 15.2138 8.17918C17.1734 5.20335 19.9633 3.0044 23.221 1.86822C27.0078 0.602926 31.0761 0.301098 35.1234 0.985149C35.2976 1.00942 35.4611 1.10654 35.5785 1.25539C35.6958 1.40425 35.7575 1.5928 35.7501 1.78007C35.7459 1.87355 35.7246 1.9638 35.6874 2.04565C35.6501 2.12749 35.5977 2.19931 35.5331 2.257C35.4685 2.31469 35.3931 2.35712 35.311 2.38184C35.2289 2.40655 35.1418 2.41307 35.0548 2.40103C31.204 1.74987 27.3331 2.03306 23.7275 3.22969C21.1007 4.15673 18.7904 5.81798 17.0181 8.05429C20.663 8.13468 24.1055 10.0777 25.906 13.1457C26.4336 13.9962 26.7898 14.9481 26.9491 15.9334C27.1084 16.9188 27.0669 17.9134 26.8276 18.8465C26.2923 20.3729 25.2504 21.5971 23.8923 22.2951C22.8483 22.9241 21.654 23.2457 20.4195 23.2302C19.185 23.2148 17.9501 22.8627 16.8288 22.2066C13.0475 19.8295 12.4823 13.8656 14.3106 9.85735C12.1048 10.5096 10.0842 11.6628 8.37741 13.2438C5.6177 15.7252 3.50336 18.9361 2.21291 22.6055C2.15115 22.7768 2.02716 22.9094 1.86802 22.9744C1.70888 23.0393 1.52753 23.0314 1.36357 22.9522C1.20079 22.8694 1.07011 22.7226 1.0001 22.5439ZM16.0682 9.53197C15.8756 9.86934 15.6946 10.2177 15.5233 10.5385C13.9608 13.9757 14.3621 18.9871 17.4556 20.9706C18.3828 21.4864 19.3963 21.7555 20.4059 21.7538C21.4155 21.7521 22.3899 21.4797 23.2423 20.9608C24.324 20.4372 25.1639 19.4928 25.6073 18.3017C25.7883 17.5692 25.8131 16.7898 25.6798 16.0197C25.5466 15.2497 25.2586 14.5082 24.8367 13.8488C23.261 11.1594 20.023 9.40744 16.7797 9.4846C16.5206 9.50411 16.2856 9.51377 16.0501 9.53934L16.0682 9.53197Z' fill='#DFEAEF'/></svg></div>";
                        break;
                    };
                    default: {
                        var confetti = "<div class='confetti' style='left:" + left + "%; animation:confetti " + duration + "s ease-in;'><svg xmlns='http://www.w3.org/2000/svg' width='15' height='16' viewBox='0 0 15 16' fill='none'><path d='M4.3689 1.70102L4.20772 5.87694L0.634194 8.15426C0.52103 8.22609 0.430148 8.3277 0.3718 8.44764C0.313451 8.56757 0.289954 8.70105 0.303958 8.83303C0.317963 8.96502 0.368912 9.09025 0.45106 9.19462C0.533208 9.29899 0.643286 9.37834 0.768888 9.42372L4.7254 10.8438L5.76617 14.8831C5.7996 15.0112 5.86844 15.1273 5.96496 15.2183C6.06148 15.3093 6.18187 15.3717 6.3126 15.3984C6.44334 15.4252 6.57925 15.4152 6.70507 15.3697C6.8309 15.3241 6.94167 15.2448 7.02493 15.1406L9.63538 11.8407L13.8405 12.0823C13.9741 12.0908 14.1077 12.0619 14.2261 11.9988C14.3444 11.9357 14.4426 11.841 14.5095 11.7255C14.5765 11.61 14.6094 11.4784 14.6046 11.3457C14.5997 11.2131 14.5573 11.0847 14.4822 10.9752L12.1663 7.48355L13.7259 3.59318C13.776 3.46986 13.7903 3.3353 13.767 3.20484C13.7437 3.07439 13.6839 2.95328 13.5943 2.85534C13.5048 2.75739 13.3891 2.68655 13.2604 2.65089C13.1318 2.61523 12.9954 2.61619 12.8668 2.65366L8.80774 3.81192L5.56113 1.14907C5.45667 1.05926 5.32801 1.00149 5.19069 0.982742C5.05337 0.963994 4.91326 0.985062 4.78723 1.04341C4.6612 1.10175 4.55465 1.19488 4.48042 1.31157C4.40619 1.42825 4.36746 1.56351 4.3689 1.70102Z' fill='#F0CC00'/></svg></div>";
                    };
                }
                $('.matching-end-block', element).append(confetti);
            }
        }

        //else record was not beaten; display current time and personal best (no need to worry about nulls since this will never be the first end page the user sees)
        else {
            var textBlock = "<div class='matching-end-standard-text-block'></div>";
            var congrats = "<div class='matching-end-congratulations'>Congratulations!</div>";
            var message = "<div class='matching-end-standard-text'>You completed the matching game in " + "<span class='matching-end-standard-time'>" + formatTime(lastPage.new_time) + "</span>" + "<br>Keep up the good work!</div>";
            var bestBlock = "<div class='matching-end-standard-best-block'></div>";
            var award = "<div class='matching-standard-award'><svg xmlns='http://www.w3.org/2000/svg' width='28' height='29' viewBox='0 0 28 29' fill='none'><path d='M22.1667 6.63411H19.8333V4.30078H8.16667V6.63411H5.83333C4.55 6.63411 3.5 7.68411 3.5 8.96745V10.1341C3.5 13.1091 5.74 15.5358 8.62167 15.8974C9.35667 17.6474 10.9317 18.9658 12.8333 19.3508V22.9674H8.16667V25.3008H19.8333V22.9674H15.1667V19.3508C17.0683 18.9658 18.6433 17.6474 19.3783 15.8974C22.26 15.5358 24.5 13.1091 24.5 10.1341V8.96745C24.5 7.68411 23.45 6.63411 22.1667 6.63411ZM5.83333 10.1341V8.96745H8.16667V13.4241C6.81333 12.9341 5.83333 11.6508 5.83333 10.1341ZM22.1667 10.1341C22.1667 11.6508 21.1867 12.9341 19.8333 13.4241V8.96745H22.1667V10.1341Z' fill='black'/></svg></div>";
            var bestText = "<div class='matching-end-standard-best-text'>Your personal best</div>";
            var bestTime = "<div class='matching-end-standard-best-time'>" + formatTime(lastPage.prev_time) + "</div>";
            var replayButton = "<div class='matching-replay-button'>Play again</div>";

            $('.matching-end-block', element).append(textBlock);
            $('.matching-end-standard-text-block', element).append(congrats);
            $('.matching-end-standard-text-block', element).append(message);
            $('.matching-end-standard-text-block', element).append(bestBlock);
            $('.matching-end-standard-best-block', element).append(award);
            $('.matching-end-standard-best-block', element).append(bestText);
            $('.matching-end-standard-best-block', element).append(bestTime);
            $('.matching-end-standard-text-block', element).append(replayButton);
        }
    }
    $(document).on('click', '.matching-container', function(eventObject) {
        var containerID = $(this).attr("id");
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'select_container'),
            data: JSON.stringify({id: containerID}),
            success: selectContainer
        });
    });

    //Reset Matching Game
    function resetMatching(initialState) {
        //Function to reset the matching game to its 'start screen' state

        $('.gamesxblock', element).empty();
        expandGame(initialState);
    }
    $(document).on('click', '.matching-replay-button', function(eventObject) {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'expand_game'),
            data: JSON.stringify({}),
            success: resetMatching
        });
    });

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