// MAPBOX APISSA LATITUDE JA LONGITUDE ON TOISINPAIN


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
var m4 = [62.230, 25.700];

var routebb = {"type":"LineString","coordinates":[[62.244, 25.736],[62.248, 25.705],[62.236, 25.715],[62.230, 25.700]]};

var marker1 = L.marker(m1).addTo(map);
var marker2 = L.marker(m2).addTo(map);
var marker3 = L.marker(m3).addTo(map);
var marker4 = L.marker(m4).addTo(map);
var route2 = {"type":"LineString","coordinates":[m1,m2,m3]};
var route3 = {"type":"LineString","coordinates":[[62.190864,25.687917],[62.190382,25.689884],[62.187495,25.696431],[62.176515,25.707875],[62.168989,25.731124],[62.158525,25.743135],[62.14971,25.763548],[62.151565,25.773137],[62.165999,25.792725],[62.172134,25.804685],[62.17734,25.81948],[62.196413,25.820974],[62.196671,25.824531]]};
marker1.bindPopup("<b>Hello malima.");
var route = {"type":"LineString","coordinates":[[25.700226,62.252873],[25.700302,62.25277],[25.700726,62.252204],[25.70153,62.251181],[25.701641,62.250946],[25.701811,62.250824],[25.704164,62.247795],[25.704223,62.24764],[25.704378,62.247525],[25.704543,62.247552],[25.704838,62.247601],[25.705474,62.247708],[25.705142,62.248163],[25.705737,62.248268],[25.705143,62.24816],[25.705474,62.247708],[25.704838,62.247601],[25.704543,62.247552],[25.704378,62.247525],[25.705209,62.246437],[25.705275,62.24632],[25.705312,62.246203],[25.705327,62.246083],[25.705318,62.245842],[25.705242,62.245256],[25.705023,62.243766],[25.705026,62.243631],[25.704928,62.243244],[25.70482,62.242994],[25.704761,62.242742],[25.704722,62.242604],[25.704699,62.24251],[25.704887,62.242528],[25.705208,62.242542],[25.705843,62.242577],[25.707366,62.242684],[25.709942,62.242836],[25.710544,62.242829],[25.711122,62.242822],[25.711562,62.2428],[25.711969,62.242771],[25.712514,62.242669],[25.712725,62.242638],[25.713047,62.242589],[25.713238,62.242642],[25.713645,62.243105],[25.71423,62.243485],[25.714716,62.243684],[25.714896,62.2438],[25.715637,62.243998],[25.71701,62.244303],[25.718041,62.244543],[25.720037,62.245111],[25.720847,62.245252],[25.721659,62.245384],[25.722029,62.245406],[25.722457,62.245429],[25.724873,62.245414],[25.725895,62.24542],[25.726733,62.245437],[25.727113,62.245432],[25.72766,62.245449],[25.727971,62.24546],[25.728326,62.24547],[25.728268,62.245339],[25.728265,62.245255],[25.728283,62.245088],[25.728118,62.244562],[25.728092,62.244482],[25.728074,62.244426],[25.727803,62.243548],[25.727783,62.243461],[25.727992,62.243459],[25.729471,62.243398],[25.731802,62.243302],[25.732025,62.243285],[25.732177,62.243267],[25.732454,62.24324],[25.732798,62.243214],[25.734179,62.243149],[25.735582,62.243092],[25.735697,62.243072],[25.735771,62.243041],[25.735798,62.243125],[25.736008,62.244]]};

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


// piirra viivatp maailmankartalle
//L.geoJson(route2).addTo(map);
geojson = route;
L.geoJson(geojson).addTo(map);
console.log(geojson.coordinates[0]);
console.log(route.coordinates[0]);

// debuggaus muuttujia
var test = liikuKohti([10,10],[15,11],11);

var kommentti1 = route.coordinates;
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
//var pisteet = [m1,m2,m3,m4];
var pisteet = route.coordinates;
var piste = pisteet[0];
var kohde = pisteet[1];
var nopeus = 0.001;



var m0 = [62.25287, 25.70022];
var m9 = [62.24816, 25.70514];

var marker0 = L.marker(m0).addTo(map);
tick();

function tick() {

    m0 = [62.249, 25.706];
    //marker.setLatLng(L.latLng(m0[0],m0[1]));

    var dx = kohde[0] - piste[0];
    var dy = kohde[1] - piste[1];
    // onko markkeri lahempana kohdetta kuin nopeus
    if (Math.sqrt(dx*dx + dy*dy) < nopeus){
	marker.setLatLng(L.latLng(kohde[1],kohde[0])); // lat long toisinpain koska api
	piste = kohde; // piste on nyt edellinen kohde
	if (++n === pisteet.length){
	    n = 0;
	}
	kohde = pisteet[n];
	
	//console.log(piste);
	//console.log(kohde);
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
//https://api.mapbox.com/v4/directions/mapbox.driving/25.705,62.218;25.735,62.244.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false

//https://api.mapbox.com/v4/directions/mapbox.driving/62.25287,25.70022;62.24816,25.70514;62.244,25.836.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false

//var m0 = [62.25287, 25.70022];
//var m9 = [62.24816, 25.70514];
//var m1 = [62.244, 25.736];
// {"type":"LineString","coordinates":[[62.244, 25.736],[62.248, 25.705],[62.236, 25.715],[62.230, 25.700]]};
//

/* 

Mapbox API:lla saa haettua tarkan reitin teitä pitkin bussipysäkiltä bussipysäkille seuraavanlaisella kyselyllä:
https://api.mapbox.com/v4/directions/mapbox.driving/25.70022,62.25287;25.70514,62.24816;25.736,62.244.json?access_token=pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q&steps=false

Access token on rekisteröity minun tunnukselle, se tulee pakosta olemaan jokseenkin julkinen ja näkymään sivun sourcessa. Käytetään sitä.
Reitissä voi olla enintään 25 pistettä kerrallaan.

Mapboxin vastaus on seuraavanlaista JSONia:
{"origin":{"type":"Feature","geometry":{"type":"Point","coordinates":[25.700225830078125,62.252872467041016]},"properties":{"name":"Laajavuorentie"}},"destination":{"type":"Feature","geometry":{"type":"Point","coordinates":[25.70514488220215,62.24816131591797]},"properties":{"name":"Tilustie"}},"waypoints":[],"routes":[{"distance":747,"duration":61,"summary":"","geometry":{"type":"LineString","coordinates":[[25.700226,62.252873],[25.700302,62.25277],[25.700726,62.252204],[25.70153,62.251181],[25.701641,62.250946],[25.701811,62.250824],[25.704164,62.247795],[25.704223,62.24764],[25.704378,62.247525],[25.704543,62.247552],[25.704838,62.247601],[25.705474,62.247708],[25.705143,62.24816]]},"steps":[]}]}

Siitä oleellisin osa on:
{"type":"LineString","coordinates":[[25.700226,62.252873],[25.700302,62.25277],[25.700726,62.252204],[25.70153,62.251181],[25.701641,62.250946],[25.701811,62.250824],[25.704164,62.247795],[25.704223,62.24764],[25.704378,62.247525],[25.704543,62.247552],[25.704838,62.247601],[25.705474,62.247708],[25.705143,62.24816]]}

,joka on tarkka reitti tietä pitkin. Sen avulla voi piirtää reitin ja liikuttaa busseja kartalla.
Yhden bussin reitti pysäkiltä pysäkille olisi siis tuota muotoa.



*/
