// Get item ID from URL parameters
const urlParams = new URLSearchParams(window.location.search);
const itemId = urlParams.get('id');

let priceChart = null;
let currentTimeFilter = 168; // Default to 1 week since we have more historical data

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    if (!itemId) {
        showError('No item ID provided');
        return;
    }
    
    loadItemDetails();
    setupTimeFilters();
});

async function loadItemDetails() {
    try {
        // Load current item data
        const currentResponse = await fetch(`http://127.0.0.1:8000/api/auctions?item_id=${itemId}`);
        const currentData = await currentResponse.json();
        
        if (currentData.length === 0) {
            showError('Item not found');
            return;
        }
        
        const item = currentData[0];
        
        // Update item header
        document.getElementById('itemName').textContent = item.name;
        document.getElementById('itemId').textContent = `Item ID: ${item.item_id}`;
        document.getElementById('itemIcon').src = item.icon_url;
        document.getElementById('itemIcon').alt = item.name;
        
        // Update stats
        const priceInGold = item.lowest_price / 10000;
        document.getElementById('currentPrice').textContent = `${priceInGold.toFixed(2)}g`;
        document.getElementById('totalQuantity').textContent = item.total_quantity.toLocaleString();
        document.getElementById('auctionCount').textContent = item.auction_count;
        
        // Load price history and create chart
        await loadPriceHistory(currentTimeFilter);
        
        // Hide loading, show content
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';
        
    } catch (error) {
        console.error('Error loading item details:', error);
        showError('Failed to load item details');
    }
}

async function loadPriceHistory(hours) {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/auctions/trends?item_id=${itemId}&hours=${hours}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('API Error:', data.error);
            return;
        }
        
        // Process data for chart
        const chartData = processChartData(data);
        createPriceChart(chartData);
        updatePriceTable(data);
        
    } catch (error) {
        console.error('Error loading price history:', error);
    }
}

function processChartData(data) {
    // Sort data by time (oldest first)
    const sortedData = data.sort((a, b) => new Date(a.hour) - new Date(b.hour));
    
    const labels = sortedData.map(item => {
        const date = new Date(item.hour);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    });
    
    const prices = sortedData.map(item => (item.min_price / 10000).toFixed(2));
    const quantities = sortedData.map(item => item.total_quantity);
    const auctionCounts = sortedData.map(item => item.auction_count);
    
    return {
        labels: labels,
        prices: prices,
        quantities: quantities,
        auctionCounts: auctionCounts,
        rawData: sortedData
    };
}

function createPriceChart(data) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (priceChart) {
        priceChart.destroy();
    }
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Average Price (Gold)',
                    data: data.prices,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Total Quantity',
                    data: data.quantities,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Price (Gold)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Quantity'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Price and Quantity History'
                },
                tooltip: {
                    callbacks: {
                        afterBody: function(context) {
                            const dataIndex = context[0].dataIndex;
                            const auctionCount = data.rawData[dataIndex].auction_count;
                            return `Auctions: ${auctionCount}`;
                        }
                    }
                }
            }
        }
    });
}

function updatePriceTable(data) {
    const tbody = document.getElementById('priceTableBody');
    tbody.innerHTML = '';
    
    // Sort data by time (newest first)
    const sortedData = data.sort((a, b) => new Date(b.hour) - new Date(a.hour));
    
    sortedData.slice(0, 20).forEach((item, index) => {
        const row = document.createElement('tr');
        
        const date = new Date(item.hour);
        const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        const priceInGold = (item.min_price / 10000).toFixed(2);
        
        // Calculate price change
        let priceChangeClass = '';
        let priceChangeText = '';
        if (index < sortedData.length - 1) {
            const currentPrice = item.min_price;
            const previousPrice = sortedData[index + 1].min_price;
            const change = currentPrice - previousPrice;
            const changePercent = ((change / previousPrice) * 100).toFixed(1);
            
            if (change > 0) {
                priceChangeClass = 'price-up';
                priceChangeText = `+${changePercent}%`;
            } else if (change < 0) {
                priceChangeClass = 'price-down';
                priceChangeText = `${changePercent}%`;
            }
        }
        
        row.innerHTML = `
            <td>${dateStr}</td>
            <td>${priceInGold}g <span class="price-change ${priceChangeClass}">${priceChangeText}</span></td>
            <td>${item.total_quantity.toLocaleString()}</td>
            <td>${item.auction_count}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function setupTimeFilters() {
    const timeButtons = document.querySelectorAll('.time-btn');
    
    timeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            timeButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get hours from data attribute
            const hours = parseInt(this.getAttribute('data-hours'));
            currentTimeFilter = hours;
            
            // Reload price history with new time filter
            loadPriceHistory(hours);
        });
    });
}

function showError(message) {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('content').style.display = 'none';
    document.getElementById('error').style.display = 'block';
    document.getElementById('error').innerHTML = `<p>${message}</p>`;
}
