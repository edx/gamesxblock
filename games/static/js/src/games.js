/* Javascript for GamesXBlock - Student View */

function GamesXBlock(runtime, element) {
    // Load cards and display them
    function loadCards() {
        $.ajax({
            type: "POST",
            url: runtime.handlerUrl(element, 'get_settings'),
            data: JSON.stringify({}),
            success: function(response) {
                console.log('Cards loaded:', response);
                displayCards(response);
            },
            error: function(xhr, status, error) {
                console.error('Error loading cards:', error);
                $('.games-container', element).html('<p class="error">Failed to load cards</p>');
            }
        });
    }

    function displayCards(data) {
        var container = $('.games-container', element);
        var html = '';
        
        if (!data.cards || data.cards.length === 0) {
            html = '<p class="no-cards">No cards available yet. Add cards in the Studio editor.</p>';
        } else {
            html += '<h3>Game Type: ' + data.game_type + '</h3>';
            html += '<div class="cards-list">';
            
            data.cards.forEach(function(card, index) {
                html += '<div class="card-item">';
                html += '<div class="card-number">Card ' + (index + 1) + '</div>';
                
                if (card.term_image) {
                    html += '<div class="card-image"><img src="' + card.term_image + '" alt="Term image"></div>';
                }
                html += '<div class="card-term"><strong>Term:</strong> ' + card.term + '</div>';
                
                if (card.definition_image) {
                    html += '<div class="card-image"><img src="' + card.definition_image + '" alt="Definition image"></div>';
                }
                html += '<div class="card-definition"><strong>Definition:</strong> ' + card.definition + '</div>';
                
                html += '</div>';
            });
            
            html += '</div>';
        }
        
        container.html(html);
    }

    // Initialize when ready
    $(function($) {
        loadCards();
    });
}
