const searchInput = document.getElementById("search");
const resultsDiv = document.getElementById("results");

let timeout = null;

searchInput.addEventListener("input", () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    const query = searchInput.value.trim();
    fetchAuctions(query);
  }, 300);
});

async function fetchAuctions(query = "") {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/auctions?query=${encodeURIComponent(query)}`);
    const data = await res.json();
    renderResults(data);
  } catch (error) {
    console.error("Error fetching auctions:", error);
  }
}

function renderResults(auctions) {
  resultsDiv.innerHTML = "";
  auctions.forEach(item => {
    const div = document.createElement("div");
    div.className = "card";
    
    const priceInGold = item.lowest_price / 10000;
    const priceDisplay = priceInGold.toFixed(2);
    
    div.innerHTML = `
      <img src="${item.icon_url}" alt="${item.name}">
      <div class="info">
        <h2>${item.name}</h2>
        <p>Price: ${priceDisplay}g</p>
        <p>Quantity: ${item.total_quantity}</p>
        <p>Auctions: ${item.auction_count}</p>
      </div>
    `;
    resultsDiv.appendChild(div);
  });
}

// Initial load
fetchAuctions();
