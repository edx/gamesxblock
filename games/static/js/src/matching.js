/* Matching game isolated script */
function GamesXBlockMatchingInit(runtime, element, pairs, matching_key) {
    const container = $('.gamesxblock-matching', element);
    const has_timer = $(container).data('timed') === true || $(container).data('timed') === 'true';

    if (!container.length || !pairs) return;

    // Prevent duplicate init that would attach multiple handlers
    if (container.data('gx_matching_initialized')) {
        return;
    }
    container.data('gx_matching_initialized', true);

    let keyMapping = null;
    let flatItems = [];

    let timerInterval = null;
    let timeSeconds = 0;

    function formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        }
        return `${minutes}:${String(secs).padStart(2, '0')}`;
    }

    function startTimer() {
        if (timerInterval) return;

        timerInterval = setInterval(function() {
            timeSeconds++;
            $('#matching-timer', element).text(formatTime(timeSeconds));
        }, 1000);
    }

    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    function refreshGame() {
        MatchInit = null;
        $.ajax({
            type: 'GET',
            url: runtime.handlerUrl(element, 'refresh_game'),
            dataType: 'html',
            success: function(html) {
                $(element).html(html);
                var decoderScript = $(element).find('#obf_decoder_script');

                if (decoderScript.length) {
                    var scriptContent = decoderScript.text();
                    decoderScript.remove();
                    try {
                        eval(scriptContent);
                        if (typeof MatchingInit === 'function') {
                            MatchingInit(runtime, element);
                        }
                    } catch (err) {
                        console.error('Failed to initialize game:', err);
                        window.location.reload();
                    }
                } else {
                    window.location.reload();
                }
            },
            error: function(xhr, status, error) {
                console.error('Failed to refresh game:', error);
                window.location.reload();
            }
        });
    }

    $('.matching-start-button', element).off('click').on('click', function() {
        if (!matching_key) {
            alert('Error: Game not initialized properly');
            return;
        }

        const spinner = $('.matching-loading-spinner', element);
        const startButton = $('.matching-start-button', element);

        spinner.addClass('active');
        startButton.prop('disabled', true);

        if (pairs && pairs.length > 0) {
            flatItems = pairs;
        }

        $.ajax({
            type: 'POST',
            url: runtime.handlerUrl(element, 'start_matching_game'),
            data: JSON.stringify({ matching_key }),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    keyMapping = response.data;
                    $('.matching-start-screen', element).remove();
                    $('.matching-grid', element).addClass('active');
                    $('.matching-footer', element).addClass('active');

                    if (has_timer) {
                        startTimer();
                    }
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

    $('.matching-end-button', element).off('click').on('click', function() {
        refreshGame();
    });

    let firstSelection = null;
    const matched = new Set();
    let matchCount = 0;
    const totalPairs = pairs.length / 2;

    function computeCircumference() {
        const circleEl = $('.matching-progress-bar', element)[0];
        if (!circleEl) return 0;
        const r = parseFloat(circleEl.getAttribute('r')) || 0;
        const svg = circleEl.ownerSVGElement;
        if (!svg) return 2 * Math.PI * r;
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

        if (matchCount >= totalPairs) {
            if (has_timer) {
                stopTimer();
            }
            setTimeout(() => {
                completeGame();
            }, 800);
        }

        setTimeout(() => {
            $([a, b]).each(function() {
                $(this).fadeOut(600, function() {
                    $(this).remove();
                });
            });
        }, 1500);
    }

    function completeGame() {
        $.ajax({
            type: 'POST',
            url: runtime.handlerUrl(element, 'complete_matching_game'),
            data: JSON.stringify({ new_time: has_timer ? timeSeconds : null }),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                // response is { new_time: int, prev_best_time: int or null }
                // if new_time is less than prev_best_time, it's a new record
                // if prev_best_time is null, it's the first completed game
                // if prev_best_time is not null and new_time >= prev_best_time, no new record

                $('.matching-end-screen', element).addClass('active');
                $('.matching-grid', element).remove();
                $('.matching-footer', element).remove();
                const { new_time, prev_best_time } = response;
                if (prev_best_time === null || new_time < prev_best_time) {
                    $('.matching-new-best', element).addClass('active');
                    $('.matching-prev-best', element).remove();
                    $('#matching-current-result', element).text(formatTime(new_time));
                    if (prev_best_time !== null) {
                        $('.matching-new-prev-best', element).addClass('active');
                        $('#matching-prev-best', element).text(formatTime(prev_best_time));
                    }
                } else {
                    $('.matching-new-best', element).remove();
                    $('.matching-prev-best', element).addClass('active');
                    $('#matching-personal-best-time', element).text(formatTime(prev_best_time));
                    $('#matching-prev-current-best-time', element).text(formatTime(new_time));
                }

                if (typeof GamesConfetti !== 'undefined') {
                    GamesConfetti.trigger($('.confetti-container', element), 20);
                }
            },
            error: function(xhr, status, error) {
                console.error('Failed to submit score:', error);
            }
        });
    }

    $('.matching-box', element).off('click').on('click', function() {
        const box = $(this);
        const dataIndex = box.data('index');

        if (!keyMapping || !flatItems.length) {
            return;
        }

        if (matched.has(dataIndex)) return;

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

        const [prevBox, prevIndex] = firstSelection;
        firstSelection = null;

        if (prevIndex === dataIndex) {
            clearSelectionVisual(prevBox);
            clearSelectionVisual(box);
            return;
        }

        const prevIdx = parseInt(prevIndex.replace('matching-key-', ''));
        const currIdx = parseInt(dataIndex.replace('matching-key-', ''));

        const prevItem = flatItems[prevIdx];
        const currItem = flatItems[currIdx];

        if (!prevItem || !currItem) {
            markIncorrect(prevBox, box);
            return;
        }

        const prevRandomKey = Object.keys(prevItem)[0];
        const currRandomKey = Object.keys(currItem)[0];

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

