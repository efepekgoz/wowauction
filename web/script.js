const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("search");
const searchBtn = document.getElementById("searchBtn");
const resultsDiv = document.getElementById("results");
const searchDropdown = document.getElementById("searchDropdown");

let searchTimeout = null;
let currentDropdownItems = [];
let selectedIndex = -1;

// Show welcome message on page load
function showWelcomeMessage() {
    resultsDiv.innerHTML = `
        <div class="welcome-message">
            <h2>Welcome to WoW Auction House</h2>
            <p>Search for items to see current auction prices and quantities.</p>
            <p>Try searching for: "linen", "cloth", "potion", "sword", etc.</p>
        </div>
    `;
}

// Show loading state
function showLoading() {
    resultsDiv.innerHTML = `
        <div class="loading">
            <p>Searching for items...</p>
        </div>
    `;
}

// Show no results message
function showNoResults(query) {
    resultsDiv.innerHTML = `
        <div class="no-results">
            <h2>No items found</h2>
            <p>No items found matching "${query}"</p>
            <p>Try a different search term.</p>
        </div>
    `;
}

// Debounced search for dropdown
function debouncedSearch(query) {
    clearTimeout(searchTimeout);
    
    if (query.length < 3) {
        hideDropdown();
        return;
    }
    
    searchTimeout = setTimeout(() => {
        fetchDropdownItems(query);
    }, 300);
}

// Fetch dropdown items
async function fetchDropdownItems(query) {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/items/search?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        currentDropdownItems = data;
        showDropdown(data);
    } catch (error) {
        console.error("Error fetching dropdown items:", error);
        hideDropdown();
    }
}

// Show dropdown with items
function showDropdown(items) {
    if (items.length === 0) {
        hideDropdown();
        return;
    }
    
    searchDropdown.innerHTML = items.map((item, index) => `
        <div class="dropdown-item" data-index="${index}">
            <img src="${item.icon_url}" alt="${item.name}">
            <span class="item-name">${item.name}</span>
        </div>
    `).join('');
    
    searchDropdown.classList.add('show');
    selectedIndex = -1;
    
    // Add click handlers
    searchDropdown.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.dataset.index);
            selectDropdownItem(index);
        });
    });
}

// Hide dropdown
function hideDropdown() {
    searchDropdown.classList.remove('show');
    selectedIndex = -1;
}

// Select dropdown item
function selectDropdownItem(index) {
    if (index >= 0 && index < currentDropdownItems.length) {
        const item = currentDropdownItems[index];
        searchInput.value = item.name;
        hideDropdown();
        // Auto-submit the search
        searchForm.dispatchEvent(new Event("submit"));
    }
}

// Handle keyboard navigation
function handleKeydown(e) {
    if (!searchDropdown.classList.contains('show')) return;
    
    const items = searchDropdown.querySelectorAll('.dropdown-item');
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateDropdownSelection(items);
            break;
        case 'ArrowUp':
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateDropdownSelection(items);
            break;
        case 'Enter':
            e.preventDefault();
            if (selectedIndex >= 0) {
                selectDropdownItem(selectedIndex);
            } else {
                searchForm.dispatchEvent(new Event("submit"));
            }
            break;
        case 'Escape':
            hideDropdown();
            break;
    }
}

// Update dropdown selection
function updateDropdownSelection(items) {
    items.forEach((item, index) => {
        item.classList.toggle('selected', index === selectedIndex);
    });
}

// Handle input changes
searchInput.addEventListener("input", (e) => {
    const query = e.target.value.trim();
    debouncedSearch(query);
});

// Handle keyboard events
searchInput.addEventListener("keydown", handleKeydown);

// Hide dropdown when clicking outside
document.addEventListener("click", (e) => {
    if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        hideDropdown();
    }
});



// Handle form submission
searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = searchInput.value.trim();
    
    if (query) {
        hideDropdown();
        searchBtn.disabled = true;
        searchBtn.textContent = "Searching...";
        showLoading();
        fetchAuctions(query);
    }
});

async function fetchAuctions(query = "") {
    try {
        const res = await fetch(`http://127.0.0.1:8000/api/auctions?query=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        if (data.length === 0) {
            showNoResults(query);
        } else {
            renderResults(data);
        }
    } catch (error) {
        console.error("Error fetching auctions:", error);
        resultsDiv.innerHTML = `
            <div class="no-results">
                <h2>Error</h2>
                <p>Failed to fetch auction data. Please try again.</p>
            </div>
        `;
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = "Search";
    }
}

function renderResults(auctions) {
    resultsDiv.innerHTML = `
        <div class="results-container">
            ${auctions.map(item => {
                const priceInGold = item.lowest_price / 10000;
                const priceDisplay = priceInGold.toFixed(2);
                
                return `
                    <div class="card" data-item-id="${item.item_id}" style="cursor: pointer;" onclick="openItemDetails(${item.item_id})">
                        <img src="${item.icon_url}" alt="${item.name}">
                        <div class="info">
                            <h2>${item.name}</h2>
                            <p>Price: ${priceDisplay}g</p>
                            <p>Quantity: ${item.total_quantity}</p>
                            <p>Auctions: ${item.auction_count}</p>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}



function openItemDetails(itemId) {
    console.log('Opening item details for ID:', itemId);
    try {
        window.open(`item.html?id=${itemId}`, '_blank');
    } catch (error) {
        console.error('Error opening item details:', error);
        // Fallback: try to navigate in same window
        window.location.href = `item.html?id=${itemId}`;
    }
}

// Make openItemDetails globally accessible
window.openItemDetails = openItemDetails;

// Test function accessibility
console.log('openItemDetails function available:', typeof window.openItemDetails);

// Show welcome message on page load
showWelcomeMessage();
