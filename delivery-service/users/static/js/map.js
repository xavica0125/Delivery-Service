let map;
let decodedPath;
let polyline, encodedPolyline;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 30.302200758628747, lng: -97.72710466785287 },
    zoom: 7,
    mapId: '4522a0646380064b'
  });
}

window.initMap = initMap;

function showPolyline(encodedPolyline, originAddressLat, originAddressLon, destinationAddressLat, destinationAddressLon) {
  // Decode the encoded polyline into LatLng coordinates
  decodedPath = google.maps.geometry.encoding.decodePath(encodedPolyline)

  // Create and add the polyline to the map
  const polyline = new google.maps.Polyline({
    path: decodedPath,
    strokeColor: "#0066CC",
    strokeOpacity: 1.0,
    strokeWeight: 4,
  });

  polyline.setMap(map); // Set the polyline on the map

  // Fit the map to the polyline bounds
  const bounds = new google.maps.LatLngBounds();
  decodedPath.forEach((point) => bounds.extend(point));
  map.fitBounds(bounds);

  const originPin = new google.maps.marker.PinElement({
    glyph: "P",
    glyphColor: "black",
  });

  const destinationPin = new google.maps.marker.PinElement({
    glyph: "D",
    glyphColor: "black",
  });

  const originAddressMarker = new google.maps.marker.AdvancedMarkerElement({
    map: map,
    position: { lat: parseFloat(originAddressLat), lng: parseFloat(originAddressLon) },
    content: originPin.element
  });

  const destinationAddressMarker = new google.maps.marker.AdvancedMarkerElement({
    map: map,
    position: { lat: parseFloat(destinationAddressLat), lng: parseFloat(destinationAddressLon) },
    content: destinationPin.element  
  });

}

document.addEventListener("htmx:afterSwap", (event) => {
  if (event.detail.target.id === "price-div") {
      const polyline = document.getElementById("polyline-data").textContent;
      const originAddressLat = document.getElementById("origin-address-latitude").textContent;
      const originAddressLon = document.getElementById("origin-address-longitude").textContent;
      const destinationAddressLat = document.getElementById("destination-address-latitude").textContent;
      const destinationAddressLon = document.getElementById("destination-address-longitude").textContent;
      
      if (polyline) {
          showPolyline(polyline.trim(), originAddressLat, originAddressLon, destinationAddressLat, destinationAddressLon);
      }
  }
});