/* Matching game isolated script */
function GamesXBlockMatchingInit(runtime, element, pairs) {
    const container = $('.gamesxblock-matching', element);
    if (!container.length || !pairs) return;

    // Guard against multiple initializations (which would attach duplicate handlers and
    // inflate matchCount making the game appear to finish early).
    if (container.data('gx_matching_initialized')) {
        return;
    }
    container.data('gx_matching_initialized', true);

    // Start screen handler
    $('.matching-start-button', element).off('click').on('click', function() {
        $('.matching-start-screen', element).hide();
        $('.matching-grid', element).addClass('active');
        $('.matching-footer', element).addClass('active');
    });

    // Build bidirectional map (term->definition and definition->term)
    const matchMap = new Map();
    pairs.forEach(p => {
        matchMap.set(p.t, p.d);
        matchMap.set(p.d, p.t);
    });

    // Track selections and matched texts
    let firstSelection = null;
    const matched = new Set();
    let matchCount = 0;
    const totalPairs = pairs.length;

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
        $('.matching-progress-text', element).text(matchCount + '/' + totalPairs);
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
        matched.add(a.text().trim());
        matched.add(b.text().trim());
        matchCount += 1;
        updateProgress();
    }

    // Ensure no duplicate click handlers remain from prior inits.
    $('.matching-box', element).off('click').on('click', function() {
        const box = $(this);
        const text = box.text().trim();
        if (matched.has(text)) return; // already matched

        // Toggle off if re-click first
        if (firstSelection && firstSelection[0].is(box)) {
            clearSelectionVisual(box);
            firstSelection = null;
            return;
        }

        box.addClass('selected');

        if (!firstSelection) {
            firstSelection = [box, text];
            return;
        }

        // Second selection
        const [prevBox, prevText] = firstSelection;
        firstSelection = null;
        if (prevText === text) {
            clearSelectionVisual(prevBox);
            clearSelectionVisual(box);
            return;
        }
        const mapped = matchMap.get(prevText);
        if (mapped && mapped === text) {
            markMatch(prevBox, box);
        } else {
            markIncorrect(prevBox, box);
        }
    });
}

