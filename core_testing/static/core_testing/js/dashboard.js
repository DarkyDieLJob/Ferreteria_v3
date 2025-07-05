/**
 * Initialize progress bars with dynamic widths
 */
function initializeProgressBars() {
    document.querySelectorAll('.progress-bar[data-width]').forEach(bar => {
        const width = bar.getAttribute('data-width');
        if (width !== null) {
            // Set the width directly with a small delay to trigger CSS transition
            setTimeout(() => {
                bar.style.width = `${width}%`;
            }, 50);
        }
    });
}

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeProgressBars();
    
    // Reinitialize progress bars if content is loaded dynamically
    const observer = new MutationObserver(function(mutations) {
        initializeProgressBars();
    });
    
    // Start observing the document with the configured parameters
    observer.observe(document.body, { childList: true, subtree: true });
});
