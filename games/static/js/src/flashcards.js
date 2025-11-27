/* Javascript for FlashcardsXBlock. */

function GamesXBlockFlashcardsInit(runtime, element, cards) {
    'use strict';

    // State
    var currentIndex = 0;
    var totalCards = cards.length;
    var flipClassName = 'flashcard-flipped';

    // DOM references
    var $element = $(element);
    var $startScreen = $element.find('.flashcards-start-screen');
    var $startButton = $element.find('.flashcards-start-button');
    var $cardWrapper = $element.find('.flashcards-card-wrapper');
    var $footer = $element.find('.flashcard-footer');
    var $card = $element.find('#flashcard-card');
    var $term = $element.find('#flashcard-term');
    var $definition = $element.find('#flashcard-definition');
    var $termImage = $element.find('#flashcard-term-image');
    var $definitionImage = $element.find('#flashcard-definition-image');
    var $progress = $element.find('#flashcard-progress');
    var $prevBtn = $element.find('#flashcard-prev');
    var $nextBtn = $element.find('#flashcard-next');

    // Render current card
    function renderCard() {
        if (totalCards === 0) return;

        var card = cards[currentIndex];

        // Update content
        $term.text(card.term || '')
        $('.flashcard-front-content').attr('title', card.term || '');
        $definition.text(card.definition || '');
        $('.flashcard-back-content').attr('title', card.definition || '');


        // Handle term image
        if (card.term_image && card.term_image.trim() !== '') {
            $termImage.attr('src', card.term_image).attr('alt', card.term).show();
        } else {
            $termImage.hide();
        }

        // Handle definition image
        if (card.definition_image && card.definition_image.trim() !== '') {
            $definitionImage.attr('src', card.definition_image).attr('alt', card.definition).show();
        } else {
            $definitionImage.hide();
        }

        // Update progress (1-indexed for display)
        $progress.text((currentIndex + 1));

        // Update button states
        $prevBtn.prop('disabled', currentIndex === 0);
        $nextBtn.prop('disabled', currentIndex === totalCards - 1);

        // Reset flip state
        if ($card.hasClass(flipClassName)) {
            $card.removeClass(flipClassName);
        }
    }

    // Flip card
    function flipCard() {
        if ($card.hasClass(flipClassName)) {
            $card.removeClass(flipClassName);
        } else {
            $card.addClass(flipClassName);
        }
    }

    // Navigation
    function goToPrev() {
        if (currentIndex > 0) {
            currentIndex--;
            renderCard();
        }
    }

    function goToNext() {
        if (currentIndex < totalCards - 1) {
            currentIndex++;
            renderCard();
        }
    }

    // Start game
    function startGame() {
        $startScreen.addClass('hidden');
        $cardWrapper.addClass('active');
        $footer.addClass('active');
        renderCard();
    }

    // Event handlers
    $startButton.on('click', function(e) {
        e.preventDefault();
        startGame();
    });

    $card.on('click', function(e) {
        e.preventDefault();
        flipCard();
    });

    $prevBtn.on('click', function(e) {
        e.preventDefault();
        goToPrev();
    });

    $nextBtn.on('click', function(e) {
        e.preventDefault();
        goToNext();
    });

    // Keyboard navigation
    $(element).on('keydown.flashcards', function(e) {
        // Only handle if flashcards is visible
        if (!$element.is(':visible')) return;

        switch(e.key) {
            case 'ArrowLeft':
                e.preventDefault();
                goToPrev();
                break;
            case 'ArrowRight':
                e.preventDefault();
                goToNext();
                break;
            case ' ':
            case 'Enter':
                e.preventDefault();
                flipCard();
                break;
        }
    });

    // Cleanup on unload
    $(element).on('remove', function() {
        $(element).off('keydown.flashcards');
    });
}
