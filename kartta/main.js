// MAPBOX APISSA LATITUDE JA LONGITUDE ON TOISINPAIN
// TODO: paivamaarat huomioon, kesa-talviaika
// onko (lon, lat) aina oikeinpain

// L on leafletin/mapboxin maarittelema
var L;
L.mapbox.accessToken = 'pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q';
// Create a map in the div #map
var map = L.mapbox.map('map', 'mikkokem.nmk0egh3');

var m1 = [62.244, 25.736];

var marker1 = L.marker(m1).addTo(map);
var route3 = {"type":"LineString","coordinates":[[62.190864,25.687917],[62.190382,25.689884],[62.187495,25.696431],[62.176515,25.707875],[62.168989,25.731124],[62.158525,25.743135],[62.14971,25.763548],[62.151565,25.773137],[62.165999,25.792725],[62.172134,25.804685],[62.17734,25.81948],[62.196413,25.820974],[62.196671,25.824531]]};
marker1.bindPopup("<b>Hello malima.");
var route = {"type":"LineString","coordinates":[[25.700226,62.252873],[25.700302,62.25277],[25.700726,62.252204],[25.70153,62.251181],[25.701641,62.250946],[25.701811,62.250824],[25.704164,62.247795],[25.704223,62.24764],[25.704378,62.247525],[25.704543,62.247552],[25.704838,62.247601],[25.705474,62.247708],[25.705142,62.248163],[25.705737,62.248268],[25.705143,62.24816],[25.705474,62.247708],[25.704838,62.247601],[25.704543,62.247552],[25.704378,62.247525],[25.705209,62.246437],[25.705275,62.24632],[25.705312,62.246203],[25.705327,62.246083],[25.705318,62.245842],[25.705242,62.245256],[25.705023,62.243766],[25.705026,62.243631],[25.704928,62.243244],[25.70482,62.242994],[25.704761,62.242742],[25.704722,62.242604],[25.704699,62.24251],[25.704887,62.242528],[25.705208,62.242542],[25.705843,62.242577],[25.707366,62.242684],[25.709942,62.242836],[25.710544,62.242829],[25.711122,62.242822],[25.711562,62.2428],[25.711969,62.242771],[25.712514,62.242669],[25.712725,62.242638],[25.713047,62.242589],[25.713238,62.242642],[25.713645,62.243105],[25.71423,62.243485],[25.714716,62.243684],[25.714896,62.2438],[25.715637,62.243998],[25.71701,62.244303],[25.718041,62.244543],[25.720037,62.245111],[25.720847,62.245252],[25.721659,62.245384],[25.722029,62.245406],[25.722457,62.245429],[25.724873,62.245414],[25.725895,62.24542],[25.726733,62.245437],[25.727113,62.245432],[25.72766,62.245449],[25.727971,62.24546],[25.728326,62.24547],[25.728268,62.245339],[25.728265,62.245255],[25.728283,62.245088],[25.728118,62.244562],[25.728092,62.244482],[25.728074,62.244426],[25.727803,62.243548],[25.727783,62.243461],[25.727992,62.243459],[25.729471,62.243398],[25.731802,62.243302],[25.732025,62.243285],[25.732177,62.243267],[25.732454,62.24324],[25.732798,62.243214],[25.734179,62.243149],[25.735582,62.243092],[25.735697,62.243072],[25.735771,62.243041],[25.735798,62.243125],[25.736008,62.244]]};

var original ={"origin":{"type":"Feature","geometry":{"type":"Point","coordinates":[25.700225830078125,62.252872467041016]},"properties":{"name":"Laajavuorentie"}},"destination":{"type":"Feature","geometry":{"type":"Point","coordinates":[25.70514488220215,62.24816131591797]},"properties":{"name":"Tilustie"}},"waypoints":[],"routes":[{"distance":747,"duration":61,"summary":"","geometry":{"type":"LineString","coordinates":[[25.700226,62.252873],[25.700302,62.25277],[25.700726,62.252204],[25.70153,62.251181],[25.701641,62.250946],[25.701811,62.250824],[25.704164,62.247795],[25.704223,62.24764],[25.704378,62.247525],[25.704543,62.247552],[25.704838,62.247601],[25.705474,62.247708],[25.705143,62.24816]]},"steps":[]}]};

var j = 0;
// L.geoJson(route).addTo(map);

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



var bussireitit =    
[{
    "reitinNimi":"kuokkala",
    "pysakinValit":[ // lista kaikista reitin pysakkien valeista
	{"lahtoNimi":"pysakki3", // pysakin nimi
	 "lahtoAika":"12:15",
	 "lahtoPiste":[62.25287, 25.70022], // [lat, lon]
	 "paateNimi":"pysakki17",
	 "paatePiste":[62.24816, 25.70514],
	 "paateAika": "12:20",
	 "duration": 300, // mapboxin reittihaun palauttama aika-arvio sekunteina
	 "coordinates":[[25.700226,62.252873],[25.700302,62.25277], 
			[25.700522,62.252304],[25.700153,62.251181],
			[25.700726,62.252204],[25.70153,62.252123]]},

	// toinen pysakkien vali esimerkiksi
	{"lahtoNimi":"pysakki17", 
	 "lahtoAika":"12:30",
	 "lahtoPiste":"[62.25334, 25.70234]",
	 "paateNimi":"pysakki68",
	 "paatePiste":[62.24816, 25.70514],
	 "paateAika": "13:15",
	 "coordinates":[[25.700226,62.252873],[25.700302,62.25277], 
			[25.700522,62.252304],[25.700153,62.251181],
			[25.700726,62.252204],[25.70153,62.252123]]}
    ] // pysakinvalit loppu
    
},
 { /* tahan toinen samanlainen reittihomma, kuten edella olevien
    * kaarisulkujen sisassa, ja loput reitit omiin sulkuihinsa */ }];

function reittiPyynto(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
	// funktiota kutsutaan kun serverin vastaus on valmis
	if (xhttp.readyState == 4 && xhttp.status == 200) {
	    serveriVastasi(xhttp.responseText);
	}
    };
    xhttp.open("GET", "/get_route?time=12:30&route=18", true); // kysyy bussien datan kello 12:30

    xhttp.send();
}

reittiPyynto();

var test = []; // debug

function serveriVastasi (vastaus) {
    console.log('valmis'); //debug
    var parsittu = JSON.parse(vastaus);


    //alert(vastaus);
    //console.log(vastaus);

    var coordinates = parsittu.pysakinValit[5].coordinates;

    var geo1;
    for (var i = 0; i < parsittu.pysakinValit.length; i++) { 
	//console.log(parsittu.pysakinValit[i].coordinates);
	coordinates = parsittu.pysakinValit[i].coordinates;
	console.log(coordinates[0]);
	
	var m1 = coordinates[i];
	L.marker([m1[1],m1[0]]).addTo(map);
	geo1 = {coordinates: coordinates, type:'LineString'};
	L.geoJson(geo1).addTo(map);
	
    }
    //coordinates.map(flip);
    var geo = {coordinates: coordinates, type:'LineString'};
    
    
    //var m1 = coordinates[0];
    //var marker1 = L.marker([m1[1],m1[0]]).addTo(map);
    //test = geo; // debug
    //alert(geo);
    L.geoJson(geo).addTo(map);
    L.geoJson(route).addTo(map);

    
    //var parsittu = JSON.parse(vastaus);
    //var parsittu = vastaus;
    // for looppi, etsi kellonajan perusteella piste missa ollaan
    // 
    //var coordinates = bussireitit[0].pysakinValit[0].coordinates;
    // seuraavaVali = bussireitit[0].pysakinValit[1].coordinates;

    // pysakinvalit indeksi, coordinaattien ajan perusteella arvioitu indeksi
    //var sijaintiReitilla = [0,4];
    // kasvata jalkimmaista kunnes length-1, sen jalkeen kasvata eka

}

// kaantaa parin toisin pain:
// flip([1,2]) -> [2,1], flip([4,5,6]) -> [5,4,6]
function flip (pair){
    var eka = pair[0];
    pair[0] = pair[1];
    pair[1] = eka;
    return pair;
}


function reittiKartalle(vastaus){
    //var parsittu = JSON.parse(vastaus);

    //alert(parsittu);
    alert(vastaus.toString());
    L.geoJson(route).addTo(vastaus);
    
}


// kertoo, onko kellonaika alku- ja loppuajan valilla
// function onkoAjanValilla(alku, loppu, aika) { /*implement*/}

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
	
    } else {
	marker.setLatLng(L.latLng(piste[1],piste[0]));
	var suuntavektori = liikuKohti(piste,kohde,nopeus);
	piste = [suuntavektori[0] + piste[0], suuntavektori[1] + piste[1]];
    }
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

// liikuttaa reitilla, reitilla monia bussipysakkeja
// reitti: [{pysakinId, pysakinNimi, saapumisaika, lahtoaika, kohdeId, }]
// reitti:lahtoNimi,lahtoAika, lahtoPiste, paateNimi, paatePiste, paateAika, duration, coordinates
var ReitillaLiikuttaja = function(reitti){
    this.reitti = reitti;
    // reitin indeksi
    this.reittino = 0;
    this.viimeksiSiirretty = null;
    this.ValillaLiikuttaja = new ValillaLiikuttaja(bussireitit[0].pysakinValit[this.reittino].coordinates);

    // palauta uusi sijainti
    this.liikuta = function(date){
        // hae daten perusteella oikea pysakki, liikuta siina tarpeeksi pitkalle
        if (this.viimeksiSiirretty === null){
            this.viimeksiSiirretty = date;
        }
        // etsi aikaa vastaava reitin piste
        // muokkaa rettino

        // ... ... ...
        

    };
    
};

// liikuttaa yhdelta pysakilta toiselle
// vali: [[lon, lat]]
var ValillaLiikuttaja = function(vali, sijainti){
    this.reitti = vali;
    var seuraavanIndeksi = 1;
    this.sijainti = sijainti; // lon, lat

    // palauta uusi sijainti
    // muuta sijaintia ja indeksia
    this.siirra = function(matka){
        var kohde = this.reitti[seuraavanIndeksi];
        var dx = kohde[0] - this.sijainti[0];
        var dy = kohde[1] - this.sijainti[1];
        var matkaKohteeseen = Math.sqrt(dx*dx + dy*dy);
        var matkaaJaljella = matkaKohteeseen - matka;
        
        var suuntavektori = [(dx / Math.sqrt(dx*dx + dy*dy))*nopeus,(dy / Math.sqrt(dx*dx + dy*dy))*nopeus];
        return suuntavektori;
    };
};
