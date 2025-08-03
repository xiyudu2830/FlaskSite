// Image carousel functionality for listings page
window.listingImages = {};
window.listingImageIndex = {};

function showImage(listingId, idx) {
    var imgs = window.listingImages[listingId];
    if (!imgs || imgs.length === 0) return;
    if (idx < 0) idx = imgs.length - 1;
    if (idx >= imgs.length) idx = 0;
    window.listingImageIndex[listingId] = idx;
    document.getElementById('listing-img-' + listingId).src = imgs[idx];
}

function initializeCarousel() {
    document.querySelectorAll('button[data-listing-id][data-direction]').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var listingId = this.getAttribute('data-listing-id');
            var direction = this.getAttribute('data-direction');
            var idx = window.listingImageIndex[listingId] || 0;
            if (direction === 'prev') {
                showImage(listingId, idx - 1);
            } else {
                showImage(listingId, idx + 1);
            }
        });
    });
}

// Global function to be called from template
window.initializeListingData = function(uploadBaseUrl) {
    document.querySelectorAll('.listing-data').forEach(function(dataDiv) {
        var listingId = dataDiv.getAttribute('data-listing-id');
        var imagesData = JSON.parse(dataDiv.getAttribute('data-images'));
        
        // Convert filenames to full URLs
        var imageUrls = imagesData.map(function(filename) {
            return uploadBaseUrl + filename;
        });
        
        window.listingImages[listingId] = imageUrls;
        window.listingImageIndex[listingId] = 0;
    });
    
    // Initialize carousel after data is loaded
    initializeCarousel();
}; 