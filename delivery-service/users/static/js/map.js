let map;
let decodedPath;
let polyline, encodedPolyline;
// Define the encoded polyline for testing (replace this with actual data)
/*const encodedPolyline = "ka_xDrvdqQSGsBPZbCFVTd@BBFHf@t@Vr@q@ZwAn@eEdBeEhBiH|CoEjBa@PeBr@sF`CiOtGuCnAuB|@iBv@_CbA{CpAkFzBeIjD{B~@sEjBcBj@o@PgCd@e@FiBRo@BcAD{BAaHOk@IyACaAAwCGo@AIV_@pB]fC]~B?HGn@c@~CcBzIY|Ag@jCiBxJARDLGXG^WN]XQF]BYFa@W[UMKc@YYUaAq@IGoEcDa@[oBwAq@Y_@GUDkHlBu@RgAX{Cx@oA\\cAXIBs@P}C~@G@wAb@SFcAXe@N[Jw@TSFuAb@mBl@iDbAg@}BG]I]Kg@Mi@AGE[]eBIa@Q}@]cB{@gEm@yCQ{@ScA}@oEWuAc@{BG[[yAYcB}A}HWmAo@cDm@sC?Ei@oBg@mAO[?AeDiGc@u@qAaCy@uAMSOW_A{Ai@_AS]]q@EIIMSi@{@cCCGm@qB_AsCqD_LOg@}BiHcAsDc@qBgBeLSyAIw@a@{CYsEMyCYaHS}Em@qNCYC{@AY]eIEm@C{@Cc@Ce@M{Ce@wKKcCIeBKcBKkAGw@I{@e@yDKu@Iu@Ga@Is@MaAWqBMgAcBeNM{@Q}A]iB]oAc@qAa@eAgAcC`@_@Z_@HKf@aANYbDiHVi@BG^{@vA}C";

async function initMap() {
  const { Map, Polyline } = await google.maps.importLibrary("maps");
  const { Geometry }  = await google.maps.importLibrary("geometry");
  // Initialize the map
  map = new Map(document.getElementById("map"), {
    center: { lat: -34.397, lng: 150.644 },
    zoom: 8,
  });

  if (Map || Polyline) {
    console.log("Google Maps other libraries are loaded.");
    
  }

  // Check if the geometry library is loaded
  if (Geometry) {
    console.log("Google Maps Geometry library is loaded.");
    return;
  }

  console.log("Geometry library loaded:", Geometry);

  // Decode the encoded polyline into LatLng coordinates
  const decodedPath = Geometry.encoding.decodePath(encodedPolyline);
  console.log("Decoded polyline:", decodedPath); // Log the decoded polyline

  // Create and add the polyline to the map
  const polyline = new Polyline({
    path: decodedPath,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2,
  });

  polyline.setMap(map); // Set the polyline on the map

  // Fit the map to the polyline bounds
  const bounds = new google.maps.LatLngBounds();
  decodedPath.forEach((point) => bounds.extend(point));
  map.fitBounds(bounds);
}

// Call initMap when the page loads
initMap();

/*async function showPolyline(encodedPolyline) {
  // Import the geometry library
  const { geometry } = await google.maps.importLibrary("geometry");
  const { Polyline } = await google.maps.importLibrary("maps");

  console.log(geometry);
  // Check if the geometry library is available
  if (!geometry || !geometry.encoding) {
      console.error("Google Maps Geometry library is not loaded.");
      return;
  }

  // Decode the encoded polyline into LatLng coordinates
  const decodedPath = geometry.encoding.decodePath(encodedPolyline);
  console.log(decodedPath); // Log the decoded polyline

  // Create and add the polyline to the map
  const polyline = new Polyline({
      path: decodedPath,
      strokeColor: "#FF0000",
      strokeOpacity: 1.0,
      strokeWeight: 2,
  });

  polyline.setMap(map); // Set the polyline on the map

  // Fit the map to the polyline bounds
  const bounds = new google.maps.LatLngBounds();
  decodedPath.forEach((point) => bounds.extend(point));
  map.fitBounds(bounds);
}*/

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