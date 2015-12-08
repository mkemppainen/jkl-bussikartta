//global kommentin tarvii, ettei emacs herjaa alustamattomista muuttujista
/* global $, L, timeOut, setInterval, clearInterval, setTimeout*/
// MAPBOX APISSA LATITUDE JA LONGITUDE ON TOISINPAIN
// TODO: paivamaarat huomioon, kesa-talviaika

// TODO: jos linjaa klikkaa liian nopeasti, piirtyy se 2 kertaa eika voi poistaa

// alustetaan kartta
L.mapbox.accessToken = 'pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q';
var map = L.mapbox.map('map', 'mikkokem.nmk0egh3');    
var bussiLayer = L.layerGroup(); // tassa layerissa on kaikki bussit
var tickInterval = 100; //millisekunteina
var test,test2,test3,test4,test5,skewer,bussi;
var currentTime = Date.parse('12:04:57'); // ohjelman aika
//var currentTime = Date.parse('12:00'); // ohjelman aika
var nykyAjassa = false; // true jos currentTime vastaa reaaliaikaa
var routes = {};
var bussit = {};
var timer; // tassa muuttujassa on kello, stopInterval(timer) pysayttaa sen
var visibleRoutes = [];

var testStops,testBussi, testRoute;

// ALOITA OHJELMA
window.onload=main;

// taman alapuolella ei pitaisi olla muuta kuin funktioita

// reitti: {"reitinNimi":,"pysakinValit:
//                           [lahtoId:,lahtoNimi:,paateID:,paateNimi:,
//                            lahtoPiste,paatePiste,duration,coordinates:[]]}
// stops: {tripId,pysahdykset:[{lahtoID,paateID,lahtoAika,paateAika}]}
// todo: muutaman sekunnin pysahdys pysakeille
// todo: bussi ottamaan layer parametri, johon bussi laitetaan
// TODO: metodi, joka nollaa liikuttajan ja siirtaa pysakkien valilla oikeaan kohtaan
// TODO: siirtonopeus huomioon (duration), siita nopeus.
// TODO: tarkista stopIndexista seuraavaa valia
// TODO: pysayta bussit tai hae lisaa stopseja kun loppuvat
var Bussi = function(reittiArg, stops){
    this.reitti = reittiArg;
    this.sijainti = [0,0];
    this.liikuttaja = null;
    this.stops = stops;
    //    this.stopIndex = etsiAika(stops,currentTime); // FIXME: palauttaa -1
    var b = this;
    this.stopIndex = 0;
//    this.reittiIndex = etsiPysakki(this.reitti, this.stops.); //tonow
    testStops = this.stops; //debug
    testRoute = this.reitti;
    printStopTimes(this.stops);
    this.marker = L.marker([0,0]).addTo(bussiLayer).bindPopup("Kaali");
    this.reittiLopussa = false;
    this.kaynnissa = false;
};

// this.stopsLopussa = false;

Bussi.prototype.paivitaStopIndex = function(){
    var index = etsiAika(this.stops,currentTime);
    this.stopIndex = index;
};

// palauta true, jos currentTime >= viimeinen aika stops listassa
// stops= yhden bussin stopit
Bussi.prototype.stopsLopussa = function(aika,stops){
    if(vertaaAikoja(currentTime, viimeinenAika(this.stops))) return true;
    return false;
};

// hakee lisaa pysakkeja stops listaan TODO
Bussi.prototype.haeLisaaPysakkeja = function(aika,stops){
    $.ajax({url: "get_stops?time=" + currentTime.toString('HH:mm:ss') +
	    "route=18",
            success: function(result){
                test2 = result;
	    },
            error: function(xhr, textStatus,error){
                test2 = xhr;
		console.log('error get_stops: var test2');
                //epaonnistui(xhr, textStatus, error);
            }
           });
};

Bussi.prototype.kaynnista = function(){
    if(this.kaynnissa) return;
    var b = this;
    this.kaynnissa = true;
    console.log('bussi kaynnistettiin reitilla: ' + b.reitti.reitinNimi);
    this.timer = setInterval(function(){b.tick();}, tickInterval);
};

Bussi.prototype.pysayta = function(){
    this.kaynnissa = false;
    clearInterval(this.timer);
};

Bussi.prototype.tick = function(){
    if (this.reittiLopussa) return; // TODO poista bussi bussiLayerista
    if (this.stopIndex < 0) {
        var lahto = this.stops.pysahdykset[0].lahtoAika;
	var vikanIndex = this.stops.pysahdykset.length - 1;
        console.log('ei loytynyt pysakin valia ajalla: ' + currentTime.toString('HH:mm:ss')); // debug
	console.log('vikan index: '+vikanIndex);
	var viimeinen = this.stops.pysahdykset[vikanIndex].paateAika;
	console.log(this.stops);
	console.log('viimenen: '+viimeinen);
        console.log('ensimmainen aika on: '+ lahto);
        console.log('viimeinen aika on: '+ viimeinen);
	console.log('');
        this.pysayta();
        var aikaAlkuun = Date.parse(lahto) - currentTime;
        console.log('odotetaan: '+aikaAlkuun/1000+'s');
        var b = this;
        setTimeout(function(){b.kaynnista();},aikaAlkuun + 100);
        return;
    }
    var coordinates = this.reitti.pysakinValit[this.stopIndex].coordinates;
    if (this.liikuttaja === null){
        this.liikuttaja = new ValillaLiikuttaja(coordinates);
        this.sijainti = coordinates[0];
        this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
    } else {
        var siirto = this.liikuttaja.siirra(0.0001); // [pos,perillaP] //TODO siirtoon oikea matka MEMO siirtonopeus
        this.sijainti = siirto[0];
        this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
	if (siirto[1]) this.seuraavaPysakki(); //
    }
};

// paivita seuraavalle pysakille
Bussi.prototype.seuraavaPysakki = function(){
    if (this.stopIndex >= this.reitti.pysakinValit.length - 1 || this.stopIndex < 0) {
	this.reittiLopussa = true;
    }
    else {
	this.stopIndex++;
	this.liikuttaja = null;
	this.paivitaStopIndex();
    } // TODO: tee reittilopussa funktio
    
//new ValillaLiikuttaja(this.reitti.pysakinValit[this.stopIndex].coordinates);
};

// etsii pysakin reitilta id:lla, palauttaa sen indeksin TONOW
function etsiPysakki(reitti, pysakinId) {
    for(var i = 0; i < reitti.pysakinValit.length; i++) {
	var p = reitti.pysakinValit[i].lahtoId;
	if (p == pysakinId) return i;
    }
}

// stops = yhden tripId:n
function printStopTimes(stops){
    for(var i = 0; i < stops.pysahdykset.length; i++) {
        console.log('Pysakinvalin indeksi: ' + i);
        console.log('lahtoAika:' + stops.pysahdykset[i].lahtoAika);
        console.log('paateAika:' + stops.pysahdykset[i].paateAika);
        console.log('jnum: ' + stops.pysahdykset[i].jnum);
    }
}


function kelloTick() {
    if (nykyAjassa || typeof currentTime === 'undefined'){
        currentTime = new Date();
    }
    else {
        currentTime.addMilliseconds(tickInterval);
    }
    asetaNakyvaAika();
}

function kelloStart() {
    timer = setInterval(kelloTick,tickInterval);

}

function kelloStop() {
    clearInterval(timer);
}

// TODO testaa
// etsii oikean pysakin, palauttaa indeksin tai -1 jos ei loydy
// stops: {tripId,pysahdykset:[{lahtoID,paateID,lahtoAika,paateAika}]}
// time: HH:mm:ss
function etsiAika(stops,time){
    if(typeof time !== 'string') time = time.toString('HH:mm:ss');
    var pysahdykset = stops.pysahdykset;
    for(var i = 0; i < pysahdykset.length; i++){
        if(vertaaAikoja(time,pysahdykset[i].lahtoAika) &&
	   !vertaaAikoja(time,pysahdykset[i].paateAika)){
	    if (i===0) return 0;
            return i;
        }
    }
    return -1;
}


//palauta  viimeinen aika yhden bussin stopseista
function viimeinenAika(stops) {
    var lastIndex = stops.pysahdykset.length - 1;
    var viimeinenAika = stops.pysahdykset[lastIndex].lahtoAika;
}

/**
 * palauta true jos time1 suurempi tai yhtasuuri kuin time2
 *  time HH:mm:ss/ h:m:s
 */
function vertaaAikoja(time1, time2){
    var t1 = time1.split(":");
    var t2 = time2.split(":");
    t1 = t1.map(Number);
    t2 = t2.map(Number);
    if (t1[0]>t2[0]) return true;
    if (t1[0]<t2[0]) return false;
    if (t1[1]>t2[1]) return true;
    if (t1[1]<t2[1]) return false;
    if (t1[2]>t2[2]) return true;
    if (t1[2]<t2[2]) return false;
    return true;
}

// liikuttaa yhdelta pysakilta toiselle
// alustetaan valin koordinaateilla, sijainti optional
// vali: [[lon, lat]]
var ValillaLiikuttaja = function(vali, sijainti) {
    this.reitti = vali;
    this.seuraavanIndeksi = 1;
    if (typeof sijainti === 'undefined') this.sijainti = vali[0];
    else this.sijainti = sijainti;
};

// siirtaa reitilla matkan verran eteenpain
// palauttaa [sijainti, matkaaJaljella, onkoPerilla]
// matkaaJaljella voi olla negatiivinen (yli lopun)
ValillaLiikuttaja.prototype.siirra = function(matkaP){
    var matka = matkaP;
    while(true){
        var kohde = this.reitti[this.seuraavanIndeksi];
        var matkaKohteeseen = pisteidenEtaisuus(this.sijainti, kohde);
        var matkaaJaljella = matkaKohteeseen - matka;
        if (matkaaJaljella < 0 ){
            if (this.seuraavanIndeksi >= this.reitti.length - 1){
		var palautus = [this.reitti[this.seuraavanIndeksi],true]; //perilla
                return palautus;
	    }
            matkaaJaljella = -matkaaJaljella;
            this.sijainti = this.reitti[this.seuraavanIndeksi];
            this.seuraavanIndeksi++;
            
            continue;
        }

        var uusiSijainti = liikuKohti(this.sijainti,kohde,matka);
        this.sijainti = uusiSijainti;
        return [uusiSijainti, false]; // ei viela perilla
    }
};

/*************** Puhtaat funktiot ******************/

// palauttaa [routeLayer, stopLayer] eli reitin ja pysakit
// routeArg = reitti (get_routen palauttama)
function teeReitti(routeArg){
    var parsittu = routeArg;
    test = parsittu;
    var routeLayer = L.mapbox.featureLayer();
    var stopLayer = L.mapbox.featureLayer();
    var route = [];
    for (var i = 0; i < parsittu.pysakinValit.length; i++) { 
        var coordinates = parsittu.pysakinValit[i].coordinates;
        route = route.concat(coordinates);
	
        // piirretaan markkerit
        var m1 = coordinates[0];
        var m0 = [m1[1],m1[0]];
        var marker0 = L.marker(m0, {
            icon: L.mapbox.marker.icon({
                'marker-symbol': i
            })
        }).addTo(stopLayer).bindPopup(parsittu.pysakinValit[i].lahtoNimi);;
    }
    
    // viimeinen pysakki
    var vika = coordinates[coordinates.length-1];
    var vika1 = [vika[1],vika[0]];
    L.marker(vika1, {
        icon: L.mapbox.marker.icon({
            'marker-symbol': i
        })
    }).addTo(stopLayer).bindPopup(parsittu.pysakinValit[i-1].paateNimi);

    var geo = {coordinates: route, type:'LineString'};
    L.geoJson(geo).addTo(routeLayer);
    
    var layerGroup = L.layerGroup();
    routeLayer.addTo(layerGroup);
    stopLayer.addTo(layerGroup);
    return layerGroup;
}

// palauttaa matkan pituuden (vektoripituutena)
// startIndex,(aloitus)sijainti optional
function matkanPituus(coordinates, sijainti, startIndex){
    var pituus = 0;
    if (typeof startIndex === 'undefined') startIndex = 0;
    if (typeof sijainti !== 'undefined') pituus = pisteidenEtaisuus(sijainti, coordinates[startIndex]);
    for (var i = startIndex; i < coordinates.length - 1; i++){
        pituus += pisteidenEtaisuus(coordinates[i],coordinates[i+1]);
    }
    return pituus;
}

// palauttaa parin kannettuna, ei muokkaa alkuperaista
// flip([1,2]) -> [2,1], flip([4,5,6]) -> [5,4]
function flip (pair){
    return [pair[1],pair[0]];
}

// palauttaa uuden sijainnin, kun liikutaan alusta kohti loppua, matkan verran
function liikuKohti(alkupiste,loppupiste,matka){
    var dx = loppupiste[0] - alkupiste[0];
    var dy = loppupiste[1] - alkupiste[1];
    var pituus = pisteidenEtaisuus(alkupiste, loppupiste);
    var vektori = [dx / pituus * matka,dy / pituus * matka];
    // TODO TODO: tassa funktiossa vikaa
    return [alkupiste[0] + vektori[0],vektori[1] + alkupiste[1]];
}

// palauta pisteiden etaisyys toisistaansa
function pisteidenEtaisuus(alku, loppu){
    var dx = loppu[0] - alku[0];
    var dy = loppu[1] - alku[1];
    return Math.sqrt(dx*dx + dy*dy);
}

/**************************************************/

function epaonnistui(xhr, textStatus, error){
    console.log(xhr.url);
    console.log(textStatus);
    console.log(error);
}

function tyhjennaReitit(){
    for (var key in routes) {
	map.removeLayer(routes[key]);
    }
}

function lisaaNakyvaReitti(reittiNro) {
	var ul = document.getElementById("routeList");
	var li = document.createElement("li");
	var cb = document.createElement("input");
	cb.type = "checkbox";
	cb.value = reittiNro;
        cb.checked = false;
        cb.id = reittiNro;
	li.appendChild(cb);
        li.innerHTML+=reittiNro;
        li.id = "li"+reittiNro;
	ul.appendChild(li);
}


function poistaNakyvaReitti(reittiNro) {
    var ul  = document.getElementById("routeList");
    ul.removeChild(document.getElementById("li"+reittiNro));
}

function piilotaReitit() {
    var poistetut = [];
    for (var i = 0; i < visibleRoutes.length; i++) {
	if (document.getElementById(visibleRoutes[i]).checked) {
	    console.log("Taulukon pituus: " + visibleRoutes.length);
	    console.log("Poistettu" + visibleRoutes[i]);
	    poistaNakyvaReitti(visibleRoutes[i]);
	    piilotaReitti(visibleRoutes[i]);
	    poistetut.push(visibleRoutes[i]);
	}
	
    }
    for (var j = 0; j < poistetut.length; j++) {
	visibleRoutes.splice(visibleRoutes.indexOf(poistetut[j]),1);
    }
}

// asettaa ajan
// aika: 'HH:mm:ss' tai Date objekti
function muutaKellonAika(aika){
    nykyAjassa = false;
    if (typeof aika === 'string') currentTime = Date.parse(aika);
    else currentTime = aika;
}

// ainoastaan paivittaa sivun kellonajan
function asetaNakyvaAika(aika){
    var aikaString;
    if (typeof aika === 'string'){ aikaString = aika; }
    else { aikaString = currentTime.toString('HH:mm:ss'); }
    $("#programtime").text(aikaString); // paivita sivun kello
}


// tekee layerin reitin numeron ja ajan perusteella
// tallentaa sen 'routes' globaaliin
function lisaaReitti(reittiNro, aika, pvm){
    if (typeof pvm === 'undefined') pvm = {vuosi:"2015", kuukausi:"12", paiva:"07"};
    if (typeof aika === 'undefined'){
	aika = currentTime.toString('HH:mm:ss');
    }
    $.ajax({
        url: "/get_route?time="+aika+"&route="+reittiNro+"&year="+pvm.vuosi+"&month="+pvm.kuukausi+"&day="+pvm.paiva,
        success: function(result){
	    test5 = result; //debug
	    var reittiPysakit = teeReitti(result);
            routes[reittiNro] = reittiPysakit;
	    if(visibleRoutes.indexOf(reittiNro) == -1) {
		visibleRoutes.push(reittiNro);
		lisaaNakyvaReitti(reittiNro);
	    }
	    //teeReitinBussit(result); // pois kommentista niin bussit piirtyvat
            
        },
        dataType: 'json',
        error: epaonnistui
    });
}

function toggleReitti(reittiNro){
    var aika = muokkaaAika(haeAnnettuAika()); 
    var aikaTeksti = aika.tunnit.toString() + ':' + aika.minuutit.toString() + ':00';

    var layer = routes[reittiNro];
    if (typeof layer === 'undefined'){
	visibleRoutes.push(reittiNro);
	lisaaNakyvaReitti(reittiNro);
	lisaaReitti(reittiNro,aikaTeksti,{vuosi:aika.vuosi, kuukausi: aika.kuukausi, paiva: aika.paiva});
	//lisaaReitti(reittiNro);
    }
    else if (map.hasLayer(layer)) {
        map.removeLayer(layer);
	visibleRoutes.splice(visibleRoutes.indexOf(reittiNro),1);
	poistaNakyvaReitti(reittiNro);
    } else {
        //map.addLayer(layer);
	layer.addTo(map);
	visibleRoutes.push(reittiNro);
	lisaaNakyvaReitti(reittiNro);
    }
}


/// Muokkaa ajan sopivaan muotoon.
function muokkaaAika(teksti){
    var re = /(\d\d)\/(\d\d)\/(\d\d\d\d) (\d\d?):(\d\d) ((PM|AM))/;//Ihanaa lukea jäkeenpäin
    var ryhmat = re.exec(teksti);
    var kuukausi;
    var paiva;
    var vuosi;
    var tunnit;
    var minuutit;
    var aamu_vai_ilta;
    
    if (ryhmat == null){
	var today = new Date();

	kuukausi = today.getMonth()+1;
	if (kuukausi < 10 ) kuukausi = '0' + kuukausi; 
	paiva = today.getDate();	
	if (paiva < 10) paiva = '0' + paiva;

	vuosi = today.getFullYear()

	tunnit = "11";//TODO Pohdi saisiko tästä järkevämmän ajan.
	minuutit = "00";

	aamu_vai_ilta = "AM";
    }
    else {
	var kuukausi = ryhmat[1];
	var paiva = ryhmat[2];
	var vuosi = ryhmat[3];
	var tunnit = ryhmat[4];
	var minuutit = ryhmat[5];
	var aamu_vai_ilta = ryhmat[6];//TODO Käsittele. Nyt ei huomioida
    }
    return {vuosi: vuosi, paiva:paiva, kuukausi:kuukausi, tunnit:tunnit,minuutit:minuutit };
}


/// Hakee annetun ajan ja palauttaa sen
function haeAnnettuAika(){
    var a = document.getElementById("time").value;
    return a;
}

// typeof reittiNro === String
// palauta onnistuttiinko
function naytaReitti(reittiNro){
    var reitti = routes[reittiNro];
    if (typeof reitti === 'undefined') return false;
    reitti.addTo(map);
    return true;
}

// typeof reittiNro === String
// palauta onnistuttiinko
function piilotaReitti(reittiNro){
    var reitti = routes[reittiNro];
    if (typeof reitti === 'undefined') return false;
    map.removeLayer(reitti);

    return true;
}

function asetaAloitusAika() {
    var dt = document.getElementById("time");
    var date = new Date();
    date.setTimeToNow();
    dt.value = date.toString("dd.MM.yyyy HH:MM");
}

// route on mallia get_route
// 
function pysahdyksetByTripId(tripId, route){
    
}



// hakee reitin stopsit ja tekee siihen bussit
function teeReitinBussit(route){
    $.ajax({url: "get_stops?time="+ currentTime.toString('HH:mm:ss')+"&route=18",
	    success: function(result){
                stopsValmis(result);
	    },
	    error: function(xhr, textStatus,error){
                test2 = xhr;
		console.log('teeBussi error get_stops: var test2');
                //epaonnistui(xhr, textStatus, error);
            }
           });

    function stopsValmis(stops){
	// TODO tee for loop tekemaan kaikki
	for(var i = 0; i < stops.matkat.length; i++) {
	    var bussi = new Bussi(route, stops.matkat[i]);
            test3 = bussi;
            bussi.kaynnista();	    
	}

    }
}


function main(){
    kelloStart();
    bussiLayer.addTo(map); // lisaa Bussit karttaan
    lisaaReitti('18');
//    lisaaNakyvaReitti('18');
//    teeReitinBussit('18');

    $(document).ready(function() {
	asetaNakyvaAika();
    });

    /*
    $.ajax({url: "get_stops?time=12:30:00&route=18",
            success: function(result){
                test2 = result;
	    },
            error: function(xhr, textStatus,error){
                test2 = xhr;
		console.log('error get_stops: var test2');
                //epaonnistui(xhr, textStatus, error);
            }
           });
     */
    /*
    //get_route
    $.ajax({
        url: "/get_route?time=18:00:00&route=18",
        success: function(result){
	    //            serveriVastasi(result);
	    var reittiPysakit = teeReitti(result);
	    var r = reittiPysakit[0].addTo(map); // reittilayer
	    var p = reittiPysakit[1].addTo(map); // pysakkilayer 
	    //map.removeLayer(p); // poistaa pysakit
	    //map.removeLayer(r); // poistaa reitin

	    featureLayer.addTo(map);
            test3=result;
            var b = new Bussi(1234, result, []);
            bussi = b;
	    setInterval(function(){b.tick();},100);
        },
        dataType: 'json',
        error: epaonnistui
    });
    //*/

}
