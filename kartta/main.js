//var myHeading = document.querySelector('h1');
//myHeading.innerHTML = 'Hello world!';
//alert("Hello! I am an alert box!!");
//var map = L.map('map').setView([51.505, -0.09], 13);
L.mapbox.accessToken = 'pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q';
// Create a map in the div #map
var map = L.mapbox.map('map', 'mikkokem.nmk0egh3');
var marker = L.marker([62.244, 25.736]).addTo(map);
var marker2 = L.marker([62.248, 25.705]).addTo(map);
marker.bindPopup("<b>Hello malima.");
//var https://api.mapbox.com/v4/directions/{profile}/{waypoints}.json?access_token=<your access token>

//var featureLayer = L.mapbox.featureLayer().loadURL('/mapbox.js/assets/data/example-single.geojson');
//featureLayer.addTo(map);

// jykyla koordinaatit: 62.244, 25.736
// jy kortepohja:       62.248, 25.705

//var https://api.mapbox.com/v4/directions/{profile}/{waypoints}.json?access_token=<your access token>
// https://api.mapbox.com/v4/directions/mapbox.driving/62.244,25.736;62.248,25.705.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false

