// Global variables for map, directions, and polyline
let map;
let directionsService;
let directionsRenderer;

// Initialize the map
function initMap() {
  // Create the map instance
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 30.302200758628747, lng: -97.72710466785287 },
    zoom: 7,
    mapId: "4522a0646380064b", 
  });

  // Initialize Directions Service and Renderer
  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({
    map: map,
  });
}

// Display the route on the map
function showRoute(originPlaceId, destinationPlaceId) {
  if (!directionsService || !directionsRenderer) {
    console.error("Directions service or renderer not initialized");
    return;
  }

  // Request route directions
  directionsService
    .route({
      origin: { placeId: originPlaceId },
      destination: { placeId: destinationPlaceId },
      travelMode: google.maps.TravelMode.DRIVING,
      provideRouteAlternatives: true,
    })
    .then((response) => {
      directionsRenderer.setDirections(response); 
    })
    .catch((error) => {
      console.error("Error fetching route directions:", error);
    });
}

// Handle HTMX afterRequest event
function handleHTMXAfterRequest(event) {
  let originPlaceId;
  let destinationPlaceId;
  
  if (event.detail.target.id === "contact-options") {
    // Extract Place IDs
    originPlaceId = document
      .getElementById("pickup_address_placeid1")
      .textContent.trim();
    destinationPlaceId = document
      .getElementById("delivery_address_placeid1")
      .textContent.trim();
  }
  else if (event.detail.target.id === "address_field_id")
  {
    originPlaceId = document
      .getElementById("pickup_address_placeid2")
      .textContent.trim();
    destinationPlaceId = document
      .getElementById("delivery_address_placeid2")
      .textContent.trim();
  }
    console.log(originPlaceId)
    console.log(destinationPlaceId)
    // Validate Place IDs
    if (originPlaceId && destinationPlaceId) {
      showRoute(originPlaceId, destinationPlaceId);
    } else {
      console.error("Invalid Place IDs provided");
    }
  
}

// Register event listeners
function setupEventListeners() {
  document.addEventListener("htmx:afterSettle", handleHTMXAfterRequest);
}

// Initialize everything
function initialize() {
  initMap(); 
  setupEventListeners();
}

window.initMap = initialize;
