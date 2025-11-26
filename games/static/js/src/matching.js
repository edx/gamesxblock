/* Matching game isolated script */
function GamesXBlockMatchingInit(runtime, element, pairs, matching_key) {
    const container = $('.gamesxblock-matching', element);
    if (!container.length || !pairs) return;

    // Guard against multiple initializations (which would attach duplicate handlers and
    // inflate matchCount making the game appear to finish early).
    if (container.data('gx_matching_initialized')) {
        return;
    }
    container.data('gx_matching_initialized', true);

    // Store for the decrypted mapping and flat items array
    let keyMapping = null;
    let flatItems = [];

    // Timer variables
    let timerInterval = null;
    let timeSeconds = 0;

    // Format time as M:SS or H:MM:SS
    function formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
        return `${minutes}:${String(secs).padStart(2, '0')}`;
    }

    // Start timer
    function startTimer() {
        if (timerInterval) return; // Prevent multiple timers

        timerInterval = setInterval(function() {
            timeSeconds++;
            $('#matching-timer', element).text(formatTime(timeSeconds));
        }, 1000);
    }

    // Stop timer
    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    // Start screen handler
    $('.matching-start-button', element).off('click').on('click', function() {
        if (!matching_key) {
            alert('Error: Game not initialized properly');
            return;
        }

        const spinner = $('.matching-loading-spinner', element);
        const startButton = $('.matching-start-button', element);

        // Show spinner, disable button
        spinner.addClass('active');
        startButton.prop('disabled', true);

        // Extract pairs (flat items) from encoded payload
        if (pairs && pairs.length > 0) {
            flatItems = pairs;
        }

        // Make API call to get key mapping
        $.ajax({
            type: 'POST',
            url: runtime.handlerUrl(element, 'get_matching_key_mapping'),
            data: JSON.stringify({ matching_key }),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    keyMapping = response.data;
                    // Remove start screen, show game
                    $('.matching-start-screen', element).remove();
                    $('.matching-grid', element).addClass('active');
                    $('.matching-footer', element).addClass('active');

                    // Start the timer
                    startTimer();
                } else {
                    alert('Error loading game: ' + (response.error || 'Unknown error'));
                    spinner.removeClass('active');
                    startButton.prop('disabled', false);
                }
            },
            error: function(xhr, status, error) {
                alert('Failed to start game. Please try again.');
                spinner.hide();
                startButton.prop('disabled', false);
            }
        });
    });

    // Track selections and matched keys
    let firstSelection = null;
    const matched = new Set();
    let matchCount = 0;
    const totalPairs = pairs.length / 2;

    // Compute real rendered circumference (accounting for viewBox scaling).
    function computeCircumference() {
        const circleEl = $('.matching-progress-bar', element)[0];
        if (!circleEl) return 0;
        const r = parseFloat(circleEl.getAttribute('r')) || 0;
        const svg = circleEl.ownerSVGElement;
        if (!svg) return 2 * Math.PI * r; // fallback
        const vbHeight = svg.viewBox && svg.viewBox.baseVal ? svg.viewBox.baseVal.height : r * 2;
        const renderedHeight = svg.getBoundingClientRect().height || vbHeight;
        const scale = vbHeight ? (renderedHeight / vbHeight) : 1;
        const effectiveR = r * scale;
        return 2 * Math.PI * effectiveR;
    }

    const baseCircumference = computeCircumference();
    if (baseCircumference) {
        $('.matching-progress-bar', element).css({
            'stroke-dasharray': baseCircumference,
            'stroke-dashoffset': baseCircumference
        });
    }

    function updateProgress() {
        $('#matching-progress-count').text(matchCount);
        const progress = totalPairs > 0 ? (matchCount / totalPairs) : 0;
        const circumference = baseCircumference || computeCircumference();
        const offset = circumference * (1 - progress);
        $('.matching-progress-bar', element).css('stroke-dashoffset', offset);
    }
    updateProgress();

    function clearSelectionVisual(box) {
        box.removeClass('selected incorrect');
    }

    function markIncorrect(a, b) {
        a.addClass('incorrect');
        b.addClass('incorrect');
        setTimeout(() => {
            clearSelectionVisual(a);
            clearSelectionVisual(b);
        }, 600);
    }

    function markMatch(a, b) {
        a.addClass('matched').removeClass('selected');
        b.addClass('matched').removeClass('selected');
        matchCount += 1;
        updateProgress();

        // Check if game is complete
        if (matchCount >= totalPairs) {
            stopTimer();
        }

        setTimeout(() => {
            $([a, b]).each(function() {
                $(this).fadeOut(600, function() {
                    $(this).remove();
                });
            });
        }, 1500);
    }

    // Ensure no duplicate click handlers remain from prior inits.
    $('.matching-box', element).off('click').on('click', function() {
        const box = $(this);
        const dataIndex = box.data('index');

        // If keyMapping not loaded yet, don't allow clicks
        if (!keyMapping || !flatItems.length) {
            return;
        }

        // Check if already matched
        if (matched.has(dataIndex)) return;

        // Toggle off if re-click first
        if (firstSelection && firstSelection[0].is(box)) {
            clearSelectionVisual(box);
            firstSelection = null;
            return;
        }

        box.addClass('selected');

        if (!firstSelection) {
            firstSelection = [box, dataIndex];
            return;
        }

        // Second selection
        const [prevBox, prevIndex] = firstSelection;
        firstSelection = null;

        // Check if same index selected
        if (prevIndex === dataIndex) {
            clearSelectionVisual(prevBox);
            clearSelectionVisual(box);
            return;
        }

        // Extract index numbers from 'matching-key-0' format
        const prevIdx = parseInt(prevIndex.replace('matching-key-', ''));
        const currIdx = parseInt(dataIndex.replace('matching-key-', ''));

        // Get randomKeys from flatItems array using indices
        const prevItem = flatItems[prevIdx];
        const currItem = flatItems[currIdx];

        if (!prevItem || !currItem) {
            markIncorrect(prevBox, box);
            return;
        }

        // Extract the randomKey from each item (first key in the object)
        const prevRandomKey = Object.keys(prevItem)[0];
        const currRandomKey = Object.keys(currItem)[0];

        // Check if pair_id matches using keyMapping
        const prevPairId = keyMapping[prevRandomKey]?.pair_id;
        const currPairId = keyMapping[currRandomKey]?.pair_id;

        if (prevPairId !== undefined && prevPairId === currPairId) {
            markMatch(prevBox, box);
            matched.add(prevIndex);
            matched.add(dataIndex);
        } else {
            markIncorrect(prevBox, box);
        }
    });
}

