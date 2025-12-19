/* Matching game isolated script */
function GamesXBlockMatchingInit(runtime, element, pages, matching_key) {
    const container = $('.gamesxblock-matching', element);
    const has_timer = $(container).data('timed') === true || $(container).data('timed') === 'true';

    if (!container.length || !pages || pages.length === 0) return;

    // Prevent duplicate init that would attach multiple handlers
    if (container.data('gx_matching_initialized')) {
        return;
    }
    container.data('gx_matching_initialized', true);

    let indexLink = null; // maps self_index -> partner_index
    let allPages = pages;
    let currentPageIndex = 0;
    let totalPages = pages.length;

    let timerInterval = null;
    let timeSeconds = 0;
    let isPreviewMode = false;

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

        $.ajax({
            type: 'POST',
            url: runtime.handlerUrl(element, 'start_matching_game'),
            data: JSON.stringify({ matching_key }),
            contentType: 'application/json',
            dataType: 'json',
            success: function(response) {
                if (response.success && response.data) {
                    const entries = response.data;
                    indexLink = {};
                    if (Array.isArray(entries)) {
                        entries.forEach((entry, selfIdx) => {
                            if (entry && typeof entry === 'string') {
                                const parts = entry.split('-');
                                if (parts.length === 5) {
                                    const indexHex = parts[1] + parts[3];
                                    indexLink[selfIdx] = parseInt(indexHex, 16);
                                }
                            }
                        });
                    }

                    // Set current page pair count
                    if (allPages && allPages[currentPageIndex]) {
                        currentPagePairs = allPages[currentPageIndex].left_items.length;
                    }

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
                if (xhr.status === 404) {
                    isPreviewMode = true;
                    indexLink = {};
                    let idx = 0;
                    allPages.forEach(page => {
                        page.left_items.forEach(() => {
                            const termIdx = idx++;
                            const defIdx = idx++;
                            indexLink[termIdx] = defIdx;
                            indexLink[defIdx] = termIdx;
                        });
                    });
                    if (allPages && allPages[currentPageIndex]) {
                        currentPagePairs = allPages[currentPageIndex].left_items.length;
                    }

                    $('.matching-start-screen', element).remove();
                    $('.matching-grid', element).addClass('active');
                    $('.matching-footer', element).addClass('active');

                    if (has_timer) {
                        startTimer();
                    }
                    spinner.removeClass('active');
                    return;
                }
                alert('Failed to start game. Please try again.');
                spinner.removeClass('active');
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
    let currentPagePairs = 0;

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
        const currentPageNumber = currentPageIndex + 1;
        $('#matching-progress-count').text(currentPageNumber);
        const progress = totalPages > 0 ? (currentPageNumber / totalPages) : 0;
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

    function loadNextPage() {
        // Increment page index
        currentPageIndex += 1;
        updateProgress();

        // Reset match count for new page
        matchCount = 0;
        matched.clear();
        firstSelection = null;

        // Get next page data
        const nextPage = allPages[currentPageIndex];
        if (!nextPage) return;

        currentPagePairs = nextPage.left_items.length;

        // Clear current boxes
        $('.matching-column-left', element).empty();
        $('.matching-column-right', element).empty();

        // Render left items
        nextPage.left_items.forEach(item => {
            const wrapper = $('<div class="matching-box-wrapper"></div>');
            const box = $('<div class="matching-box"></div>')
                .attr('data-index', `matching-key-${item.index}`)
                .attr('title', item.text);
            const text = $('<span class="matching-box-text"></span>').text(item.text);
            box.append(text);
            wrapper.append(box);
            $('.matching-column-left', element).append(wrapper);
        });

        // Render right items
        nextPage.right_items.forEach(item => {
            const wrapper = $('<div class="matching-box-wrapper"></div>');
            const box = $('<div class="matching-box"></div>')
                .attr('data-index', `matching-key-${item.index}`)
                .attr('title', item.text);
            const text = $('<span class="matching-box-text"></span>').text(item.text);
            box.append(text);
            wrapper.append(box);
            $('.matching-column-right', element).append(wrapper);
        });

        // Re-attach click handlers to new boxes
        attachBoxClickHandlers();
    }

    function markMatch(a, b) {
        a.addClass('matched').removeClass('selected');
        b.addClass('matched').removeClass('selected');
        matchCount += 1;

        // Check if current page is complete
        if (matchCount >= currentPagePairs) {
            // Check if there are more pages
            if (currentPageIndex + 1 < totalPages) {
                loadNextPage();
            } else {
                // All pages complete - end game
                if (has_timer) {
                    stopTimer();
                }
                setTimeout(() => {
                    completeGame();
                }, 800);
            }
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
        if (!has_timer) {
            $('.matching-end-screen', element).addClass('active');
            $('.matching-non-timer', element).addClass('active');
            $('.matching-new-best', element).remove();
            $('.matching-prev-best', element).remove();
            $('.matching-grid', element).remove();
            $('.matching-footer', element).remove();
            if (typeof GamesConfetti !== 'undefined') {
                GamesConfetti.trigger($('.confetti-container', element), 20);
            }
            return;
        }

        // In preview mode, skip server call and show completion directly
        if (isPreviewMode) {
            $('.matching-end-screen', element).addClass('active');
            $('.matching-grid', element).remove();
            $('.matching-footer', element).remove();
            $('.matching-new-best', element).addClass('active');
            $('.matching-prev-best', element).remove();
            $('#matching-current-result', element).text(formatTime(timeSeconds));
            $('.matching-new-prev-best', element).remove();

            if (typeof GamesConfetti !== 'undefined') {
                GamesConfetti.trigger($('.confetti-container', element), 20);
            }
            return;
        }

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

    function handleBoxClick() {
        const box = $(this);
        if (!indexLink) return;
        const idxStr = box.data('index');
        if (!idxStr) return;
        const idx = parseInt(idxStr.replace('matching-key-', ''), 10);
        if (Number.isNaN(idx)) return;
        if (matched.has(idx)) return;

        if (firstSelection && firstSelection[0].is(box)) {
            clearSelectionVisual(box);
            firstSelection = null;
            return;
        }

        box.addClass('selected');
        if (!firstSelection) {
            firstSelection = [box, idx];
            return;
        }

        const [prevBox, prevIdx] = firstSelection;
        firstSelection = null;
        if (prevIdx === idx) {
            clearSelectionVisual(prevBox);
            clearSelectionVisual(box);
            return;
        }

        const partnerOfPrev = indexLink[prevIdx];
        const partnerOfCurr = indexLink[idx];
        if (partnerOfPrev === idx && partnerOfCurr === prevIdx) {
            markMatch(prevBox, box);
            matched.add(prevIdx);
            matched.add(idx);
        } else {
            markIncorrect(prevBox, box);
        }
    }

    function attachBoxClickHandlers() {
        $('.matching-box', element).off('click').on('click', handleBoxClick);
    }

    attachBoxClickHandlers();
}

