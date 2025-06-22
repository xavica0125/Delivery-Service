// Global variables for map, directions, and polyline
let map;
let directionsService;
let directionsRenderer;
let oldMarkers = [];
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

  if(oldMarkers.length > 0) // Remove currently visible markers from map
  {
    for(let i = 0; i < oldMarkers.length; i++)
    {
      oldMarkers[i].map = null;
    };
  }

  oldMarkers = [];

  const [originCoords, destinationCoords] = await Promise.all([getCoordinates("pickup_address"), getCoordinates("delivery_address")]);

  // Request route directions
  directionsService
    .route({
      origin: { placeId: originPlaceId },
      destination: { placeId: destinationPlaceId },
      travelMode: google.maps.TravelMode.DRIVING,
      provideRouteAlternatives: true,
    })
    .then((response) => {
      createMarker(originCoords, "green", "origin");
      createMarker(destinationCoords, "red", "destination");
      directionsRenderer.setDirections(response);
      //directionsRenderer.setRouteIndex(1);  Sets alternative route if there are any
      
    })
    .catch((error) => {
      console.error("Error fetching route directions:", error);
    });
}

// Make custom marker elements to display alongside route

function createMarker(coords, color, markerType) {
  const parser = new DOMParser();
  let pinSvgString;
  if(markerType === "origin")
  {
    pinSvgString = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-house-fill' viewBox='0 0 16 16'> <path d='M8.707 1.5a1 1 0 0 0-1.414 0L.646 8.146a.5.5 0 0 0 .708.708L8 2.207l6.646 6.647a.5.5 0 0 0 .708-.708L13 5.793V2.5a.5.5 0 0 0-.5-.5h-1a.5.5 0 0 0-.5.5v1.293z'/> <path d='m8 3.293 6 6V13.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5V9.293z'/> </svg>";
  }
  else
  {
    pinSvgString = "<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='currentColor' class='bi bi-flag-fill' viewBox='0 0 16 16'> <path d='M14.778.085A.5.5 0 0 1 15 .5V8a.5.5 0 0 1-.314.464L14.5 8l.186.464-.003.001-.006.003-.023.009a12 12 0 0 1-.397.15c-.264.095-.631.223-1.047.35-.816.252-1.879.523-2.71.523-.847 0-1.548-.28-2.158-.525l-.028-.01C7.68 8.71 7.14 8.5 6.5 8.5c-.7 0-1.638.23-2.437.477A20 20 0 0 0 3 9.342V15.5a.5.5 0 0 1-1 0V.5a.5.5 0 0 1 1 0v.282c.226-.079.496-.17.79-.26C4.606.272 5.67 0 6.5 0c.84 0 1.524.277 2.121.519l.043.018C9.286.788 9.828 1 10.5 1c.7 0 1.638-.23 2.437-.477a20 20 0 0 0 1.349-.476l.019-.007.004-.002h.001'/></svg>"
  }
  const pinSvg = parser.parseFromString(
    pinSvgString,
    "image/svg+xml",
  ).documentElement;
  
  const pin = new google.maps.marker.PinElement({
    scale : 1,
    background : color,
    borderColor : color,
    glyph: pinSvg,
    glyphColor : "white"
  });

  const marker = new google.maps.marker.AdvancedMarkerElement({
    map : map,
    position : {lat : coords[0], lng : coords[1]},
    content : pin.element
  });

  oldMarkers.push(marker);
}


// Utilize Google Maps Geocoding to get coordinates to origin and destination addresses

async function getCoordinates(address) {
  let coordinates = []
  coordinates.push(parseFloat(document.getElementById(address).selectedOptions[0].dataset.latitude));
  coordinates.push(parseFloat(document.getElementById(address).selectedOptions[0].dataset.longitude)); 

  return coordinates;
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
