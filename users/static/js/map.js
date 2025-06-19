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
    suppressMarkers : true
  });
}

// Display the route on the map
 async function showRoute(originPlaceId, destinationPlaceId) {
  if (!directionsService || !directionsRenderer) {
    console.error("Directions service or renderer not initialized");
    return;
  }
  const [originCoords, destinationCoords] = await Promise.all([getCoordinates(originPlaceId), getCoordinates(destinationPlaceId)]);
  /*const params = new URLSearchParams({
    'originPlaceID' : originPlaceId,
    'destinationPlaceID' : destinationPlaceId
  });

  

  fetch(`/calculate_route/?${params.toString()}`)
  .then(response => response.json())
  .then(data => {
    for(let i = 0; i < data.routes.length; i++)
    {
      createPolyline(data.routes[i].polyline.encodedPolyline);
    }

    console.log(data.routes.length);
  })
  .catch(error => console.error("Error:", error));*/

  // Request route directions
  directionsService
    .route({
      origin: { placeId: originPlaceId },
      destination: { placeId: destinationPlaceId },
      travelMode: google.maps.TravelMode.DRIVING,
      provideRouteAlternatives: true,
      drivingOptions : {
        trafficModel : 'bestguess',
        departureTime : new Date()
      }
    })
    .then((response) => {
      createMarker(originCoords, "green");
      createMarker(destinationCoords, "red");
      directionsRenderer.setDirections(response);
      directionsRenderer.setRouteIndex(1);
      
    })
    .catch((error) => {
      console.error("Error fetching route directions:", error);
    });
}

function createPolyline(encodedPolyline) {
  const decodedPath = google.maps.geometry.encoding.decodePath(encodedPolyline);

  const polyline = new google.maps.Polyline({
    path: decodedPath,
    strokeColor: "#0066CC",
    strokeOpacity: 1.0,
    strokeWeight: 4,
  });

  polyline.setMap(map);
}

// Make custom marker elements to display alongside route

function createMarker(coords, color) {
  const pin = new google.maps.marker.PinElement({
    scale : 1,
    background : color,
    borderColor : color,
    glyphColor: "white",
  });

  const marker = new google.maps.marker.AdvancedMarkerElement({
    map : map,
    position : coords,
    content : pin.element
  });

}


// Utilize Google Maps Geocoding to get coordinates to origin and destination addresses

async function getCoordinates(placeId) {
  const geocoder = new google.maps.Geocoder();
  
  const geocodeResponse = await geocoder.geocode({
    placeId : placeId
  });

  return geocodeResponse.results[0]["geometry"]["location"];
}

// Handle HTMX afterRequest event
function handleMapRouting() {
  let originPlaceId = document.getElementById("pickup_address").selectedOptions[0].dataset.placeid;
  let destinationPlaceId = document.getElementById("delivery_address").selectedOptions[0].dataset.placeid;

    // Validate Place IDs
  if (originPlaceId && destinationPlaceId) {
    showRoute(originPlaceId, destinationPlaceId);
  } else {
    console.error("Invalid Place IDs provided");
  }
  
}

// Register event listeners
function setupEventListeners() {
  pickup_address = document.getElementById("pickup_address");
  delivery_address = document.getElementById("delivery_address");

  pickup_address.addEventListener("change", handleMapRouting);
  delivery_address.addEventListener("change", handleMapRouting);
  
  const swap_button = document.getElementById("swap-button");

  swap_button.addEventListener("click", swapValues);
  
}

function swapValues()
{
    let pickup_address = document.getElementById("pickup_address").value; //DO NOT FORGET, I moved pickup and delivery address inside swapValues function to update it everytime the values are changed
    let delivery_address = document.getElementById("delivery_address").value;

    let temp = pickup_address;

    pickup_address = delivery_address;
    delivery_address = temp;

    document.getElementById("pickup_address").value = pickup_address;
    document.getElementById("delivery_address").value = delivery_address;

    htmx.ajax('GET', "/contact_options", {target: "#contact-options", values: {
      "delivery_address" : delivery_address
    }});

    handleMapRouting();
}

// Initialize everything
function initialize() {
  initMap(); 
  setupEventListeners();
}

window.initMap = initialize;
