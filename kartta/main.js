//var myHeading = document.querySelector('h1');
//myHeading.innerHTML = 'Hello world!';
//alert("Hello! I am an alert box!!");
//var map = L.map('map').setView([51.505, -0.09], 13);
L.mapbox.accessToken = 'pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q';
// Create a map in the div #map
var map = L.mapbox.map('map', 'mikkokem.nmk0egh3');
var m1 = [62.244, 25.736];
var m2 = [62.248, 25.705];
var m3 = [62.236, 25.715];
var marker1 = L.marker(m1).addTo(map);
var marker2 = L.marker(m2).addTo(map);
var marker3 = L.marker(m3).addTo(map);
var route = {"type":"LineString","coordinates":[m1,m2,m3]};

marker1.bindPopup("<b>Hello malima.");
//route = JSON.parse(route);

// Generate a GeoJSON line. You could also load GeoJSON via AJAX
// or generate it some other way.
var geojson = { type: 'LineString', coordinates: [] };
var start = [10, 20];
var momentum = [3, 3];


// tee epamaaraiset viivat maailmankartalle
for (var i = 0; i < 300; i++) {
    start[0] += momentum[0];
    start[1] += momentum[1];
    if (start[1] > 60 || start[1] < -60) momentum[1] *= -1;
    if (start[0] > 170 || start[0] < -170) momentum[0] *= -1;
    geojson.coordinates.push(start.slice());}

// piirra viivat maailmankartalle
L.geoJson(geojson).addTo(map);

// debuggaus muuttujia
var test = liikuKohti([10,10],[15,11],11);

var kommentti1 = test;
var kommentti2 = route.coordinates[0];
var kommentti3 = route.coordinates[0][0];

// testiiiiiiiiii
// document.getElementById('teksti').innerHTML = '<p>'+ route.coordinates + '</p>';
var mydiv = document.getElementById("teksti");
mydiv.appendChild(document.createTextNode(kommentti1 + "_________"));
mydiv.appendChild(document.createTextNode(kommentti2 + "_________"));
mydiv.appendChild(document.createTextNode(kommentti3));




// Create a counter with a value of 0.
var j = 0;

// Create a marker and add it to the map.
var marker = L.marker(m1, {
  icon: L.mapbox.marker.icon({
    'marker-color': '#f86767'
  })
}).addTo(map);

// testiiiii
//document.getElementById('teksti').innerHTML = '<p>'+ route + '</p>';
var n = 0;
var pisteet = [m1,m2,m3];
var piste = pisteet[0];
var kohde = pisteet[1];
var nopeus = 0.001;
tick();

function tick() {
    onTick();
}

function onTick() {
    var dx = kohde[0] - piste[0];
    var dy = kohde[1] - piste[1];
    // onko markkeri lahempana kohdetta kuin nopeus
    if (Math.sqrt(dx*dx + dy*dy) < nopeus){
	marker.setLatLng(L.latLng(kohde[0],kohde[1])); // suoraan kohteeseen
	piste = kohde; // piste on nyt edellinen kohde
	if (++n === pisteet.length){
	    n = 0;
	}
	kohde = pisteet[n];
	
	console.log(piste);
	console.log(kohde);
    } else {
    marker.setLatLng(L.latLng(piste[0],piste[1]));
    var suuntavektori = liikuKohti(piste,kohde,nopeus);
    piste = [suuntavektori[0] + piste[0], suuntavektori[1] + piste[1]];
    }
  
//    marker.setLatLng(L.latLng(
//        route.coordinates[j][0],
//        route.coordinates[j][1]));

    // Move to the next point of the line
    // until `j` reaches the length of the array.
    //if (++j < route.coordinates.length)
    setTimeout(tick, 100);
}

// palauttaa suuntavektorin, kun liikutaan kohti toista pistetta tietylla nopeudella
// lisaamalla suuntavektorin koordinaatteihin saa seuraavan sijainnin
function liikuKohti(alkupiste,loppupiste,nopeus){
    var dx = loppupiste[0] - alkupiste[0];
    var dy = loppupiste[1] - alkupiste[1];
    var suuntavektori = [(dx / Math.sqrt(dx*dx + dy*dy))*nopeus,(dy / Math.sqrt(dx*dx + dy*dy))*nopeus];
    return suuntavektori;
}


//document.getElementById('teksti').innerText = '<p> ' + 'Some Text' + ' </p>'; //
//var https://api.mapbox.com/v4/directions/{profile}/{waypoints}.json?access_token=<your access token>

//var featureLayer = L.mapbox.featureLayer().loadURL('/mapbox.js/assets/data/example-single.geojson');
//featureLayer.addTo(map);

// jykyla koordinaatit: 62.244, 25.736
// jy kortepohja:       62.248, 25.705

//var https://api.mapbox.com/v4/directions/{profile}/{waypoints}.json?access_token=<your accestss token>
// https://api.mapbox.com/v4/directions/mapbox.walking/62.218,25.705;62.244,25.736;62.248,25.733.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false



