// ===============================
// Grab elements from the page
// ===============================
const searchForm = document.getElementById("searchForm");
const resultsDiv = document.getElementById("results");

// ===============================
// Initialize Leaflet Map
// ===============================
const map = L.map('map').setView([-1.2921, 36.8219], 12); // Nairobi default

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors'
}).addTo(map);

let markers = []; // keep track of pins

// ===============================
// Handle search form submit
// ===============================
searchForm.addEventListener("submit", async function(e){
  e.preventDefault();

  const location = document.getElementById("location").value;
  const price = document.getElementById("price").value;
  const size = document.getElementById("size").value;

  const params = new URLSearchParams();
  if (location) params.append('location', location);
  if (price) {
    // Parse price range (e.g., "10000-20000" or "100000+")
    if (price.includes('-')) {
      const [min, max] = price.split('-');
      params.append('min_price', min);
      params.append('max_price', max);
    } else if (price.includes('+')) {
      const min = price.replace('+', '');
      params.append('min_price', min);
    } else {
      params.append('min_price', price);
    }
  }
  if (size) params.append('bedrooms', size);

  try {
    const apiBase = (window.location.protocol.startsWith('http') && !['5500', '3000', '5173'].includes(window.location.port))
        ? window.location.origin
        : 'http://localhost:8080';
    const res = await fetch(`${apiBase}/api/properties/?${params.toString()}`);
    const houses = await res.json();
    displayResults(houses);
  } catch (error) {
    console.error("Error fetching houses:", error);
    resultsDiv.innerHTML = "<p style='color:red;'>Error fetching houses. Please check backend.</p>";
  }
});

// ===============================
// Show results (cards + map pins)
// ===============================
function displayResults(list) {
  resultsDiv.innerHTML = "";

  // 1. Clear old markers
  markers.forEach(m => map.removeLayer(m));
}

async function payWithMpesa(phone, amount) {
  try {
    const apiBase = (window.location.protocol.startsWith('http') && !['5500', '3000', '5173'].includes(window.location.port))
        ? window.location.origin
        : 'http://localhost:8080';
    const res = await fetch(`${apiBase}/api/properties/pay/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone, amount }),
    });
    const data = await res.json();
    console.log("Payment response:", data);

    alert("STK Push sent to your phone. Please enter your M-Pesa PIN.");
  } catch (err) {
    console.error("Payment error:", err);
    alert("Payment failed. Please try again.");
  }
}

