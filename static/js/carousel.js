// Image carousel functionality for listings page
window.listingImages = {};
window.listingImageIndex = {};

// Function to show image at specific index
function showImage(listingId, idx) {
    var imgs = window.listingImages[listingId];
    if (!imgs || imgs.length === 0) return;
    if (idx < 0) idx = imgs.length - 1;
    if (idx >= imgs.length) idx = 0;
    window.listingImageIndex[listingId] = idx;
    document.getElementById('listing-img-' + listingId).src = imgs[idx];
}

// Initialize carousel functionality
function initializeCarousel() {
    // Set up event listeners for navigation buttons
    var buttons = document.querySelectorAll('button[data-listing-id][data-direction]');
    console.log('Found buttons:', buttons.length);
    
    buttons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var listingId = this.getAttribute('data-listing-id');
            var direction = this.getAttribute('data-direction');
            var idx = window.listingImageIndex[listingId] || 0;
            console.log('Button clicked:', listingId, direction, idx);
            console.log('Available images:', window.listingImages[listingId]);
            if (direction === 'prev') {
                showImage(listingId, idx - 1);
            } else {
                showImage(listingId, idx + 1);
            }
        });
        
        // Add hover effect for better UX
        btn.addEventListener('mouseenter', function() {
            this.style.opacity = '1';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.opacity = '0.8';
        });
    });
    
    console.log('Carousel initialized with listings:', Object.keys(window.listingImages));
    console.log('Total buttons found:', document.querySelectorAll('button[data-listing-id][data-direction]').length);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for data to be initialized
    setTimeout(initializeCarousel, 100);
}); 