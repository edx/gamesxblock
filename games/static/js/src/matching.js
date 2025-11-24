/* Matching game isolated script */
function GamesXBlockMatchingInit(runtime, element, pairs) {
    const container = $('.gamesxblock-matching', element);
    if (!container.length || !pairs) return;

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

    function updateProgress() {
        $('.matching-progress-text', element).text(matchCount + '/' + totalPairs);
        // Update circular progress bar (circumference = 2 * π * r = 2 * π * 54 ≈ 339.292)
        const circumference = 339.292;
        const progress = totalPairs > 0 ? (matchCount / totalPairs) : 0;
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

    $('.matching-box', element).on('click', function() {
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

