let map;
let decodedPath;
let polyline, encodedPolyline;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
    mapId: '4522a0646380064b'
  });


}

window.initMap = initMap;

function showPolyline(encodedPolyline) {

  decodedPath = google.maps.geometry.encoding.decodePath(encodedPolyline)



  // Decode the encoded polyline into LatLng coordinates

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

  const pin = new google.maps.marker.PinElement({
    scale: 1.5,
});

  const advancedMarker = new google.maps.marker.AdvancedMarkerElement({
    map: map,
    position: { lat: 30.3106128, lng: -97.3500027 },
    content: pin.element
  });

  
  /*const content = advancedMarker.content;

  content.style.opacity = "0";
  content.addEventListener("animationend", (event) => {
    content.classList.remove("drop");
    content.style.opacity = "1";
  });

  const time = 2 + Math.random(); // 2s delay for easy to see the animation

  content.style.setProperty("--delay-time", time + "s");
  */
}

document.addEventListener("htmx:afterSwap", (event) => {
  console.log("htmx:afterSwap event triggered");
  console.log("hello");
  if (event.detail.target.id === "price-div") {
      const polyline = document.getElementById("polyline-data").textContent;
      console.log(polyline);
      if (polyline) {
          showPolyline(polyline.trim());
      }
  }
});