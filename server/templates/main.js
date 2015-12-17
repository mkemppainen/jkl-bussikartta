//global kommentin tarvii, ettei emacs herjaa alustamattomista muuttujista
/* global $, L, timeOut, setInterval, clearInterval, setTimeout*/
// MAPBOX APISSA LATITUDE JA LONGITUDE ON TOISINPAIN
// TODO: paivamaarat huomioon, kesa-talviaika

// TODO: jos linjaa klikkaa liian nopeasti, piirtyy se 2 kertaa eika voi poistaa
// TODO: kun klikkaa markkeria, piirretaan sen reitti
// TODO: functio, jolla liittaa, stop
// /get_single_route?stop1=207523&stop2=207532
// alustetaan kartta
L.mapbox.accessToken = 'pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q';
var map = L.mapbox.map('map', 'mikkokem.nmk0egh3');
var reittiLayer = L.layerGroup().addTo(map);
var bussiLayer = L.layerGroup().addTo(map); // tassa layerissa on kaikki bussit
var tickInterval = 100; //millisekunteina
var test,test2,test3,test4,test5,skewer,bussi;
//var currentTime = Date.parse('23:59:54'); // ohjelman aika
var currentTime = new Date(); // ohjelman aika
var nykyAjassa = true; // true jos currentTime vastaa reaaliaikaa
var routes = {};
var bussit = [];
var timer; // tassa muuttujassa on kello, stopInterval(timer) pysayttaa sen
var visibleRoutes = [];
var bussiLista = [];
var bussiIcon = L.icon({
    iconUrl: '/static/bussi3.png',
    iconSize: [30, 30]
});
var bussiIconHarmaa = L.icon({
    iconUrl: '/static/bussi-harmaa.png',
    iconSize: [30, 30]
});
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

// TODO jotkin bussit ei liiku ollnkaan, tarkista miksi pysahtyy
// TODO: //.addTo(bussiLayer).bindPopup("Kaali"); TODO lisaa toisaalla layeriin
// kaynnista funktio eri funktioon, kuin milla bussi alunperin kaynnistetaan
var Bussi = function(reittiArg, stops){
    this.reitti = reittiArg;
    this.sijainti = [0,0];
    this.liikuttaja = null;
    this.stops = stops;
    var b = this;
    this.stopIndex = etsiAika(this.stops,currentTime);
    this.reittiIndex = etsiPysakki(this.reitti, this.stops.pysahdykset[Math.max(0,this.stopIndex)].lahtoID);
    testStops = this.stops; //debug
    testRoute = this.reitti; //debug
    testBussi = this;
    //printStopTimes(this.stops);
    this.marker = L.marker([0,0]).addTo(bussiLayer).bindPopup('Linja: ' + reittiArg.reitinNimi); //TODO lisaa toisaalla layeriin
    bussiLista.push(this);
    this.marker.setIcon(bussiIcon);
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

// TODO: onko paate 
// hakee lisaa pysakkeja stops listaan TODO
Bussi.prototype.haeLisaaPysakkeja = function(aika,stops){
    $.ajax({url: "get_stops?time=" + aika.tunnit + ":" + aika.minuutit + ":00" /*currentTime.toString('HH:mm:ss')*/ +
	    "route=" + this.reitti.reitinNimi,
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
    this.marker.bindPopup('Linja: ' + this.reitti.reitinNimi);
    this.marker.setIcon(bussiIcon);
    var b = this;
    this.kaynnissa = true;
    this.timer = setInterval(function(){b.tick();}, tickInterval);
};

Bussi.prototype.pysayta = function(){
    this.kaynnissa = false;
    clearInterval(this.timer);
};

Bussi.prototype.tick = function() {

    if (this.stopIndex < 0) {
    	this.ehkaOdota();
        var lahto2 = this.stops.pysahdykset[0].lahtoAika;
    	var vikanIndex = this.stops.pysahdykset.length - 1;
    	var viimeinen = this.stops.pysahdykset[vikanIndex].paateAika;
        this.pysayta();
        var aikaAlkuun = Date.parse(lahto2) - currentTime;
        if (aikaAlkuun < 0){
            this.reittiLopussa = true;
            return;
        }
        var b = this;
        setTimeout(function(){b.kaynnista();},aikaAlkuun + 100);
        return;
        }
    
    this.reittiIndex = etsiPysakki(this.reitti, this.stops.pysahdykset[Math.max(0,this.stopIndex)].lahtoID);

    if (this.reittiLopussa) {
	this.poista();
	return;
    }
    
    if (this.reittiIndex < 0) { // ei loytynyt pysakkia jolla ollaan
        this.reitti = {pysakinValit:[],reitinNimi:this.reitti.reitinNimi};
        var lahto = this.stops.pysahdykset[this.stopIndex].lahtoID;
        var paate = this.stops.pysahdykset[this.stopIndex].paateID;
        if (lahto == paate){
            this.reittiLopussa = true;
            return;
        }
        this.pysayta();
        this.haePysakki(lahto,paate,this);
        this.reittiIndex = 0;
        return;
    }

    var coordinates = this.reitti.pysakinValit[this.reittiIndex].coordinates;
    this.ehkaOdota();
    if (this.liikuttaja === null){
        this.liikuttaja = new ValillaLiikuttaja(coordinates);
        this.sijainti = coordinates[0];
        this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
    } else {
        var duration = this.reitti.pysakinValit[this.reittiIndex].duration;
        var matka = matkanPituus(this.reitti.pysakinValit[this.reittiIndex].coordinates);
        var siirtoMatka = 0.75 * siirtoPerTick(duration,matka,tickInterval); // puolitetaan nopeus
        var siirto = this.liikuttaja.siirra(siirtoMatka); // [pos,perillaP] //TODO siirtoon oikea matka MEMO siirtonopeus
        this.sijainti = siirto[0];
        this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
	if (siirto[1]) this.seuraavaPysakki(); //
    }
};

// odota, jos pysakilta nykyinen aika alle pysakilta lahtoajan
// TODO: laita timeoutin sijaan bussit listaan, laita this.lahtoaika
Bussi.prototype.ehkaOdota = function (){
    var i = Math.max(0,this.stopIndex);
    var vikanIndex = this.stops.pysahdykset.length - 1;
    if (i > vikanIndex) {
        this.pysayta();
        console.log('stops loppu, pysaytetaan');
    }
    var lahto = this.stops.pysahdykset[i].lahtoAika;
    var aikaAlkuun = Date.parse(lahto) - currentTime;
    if (aikaAlkuun <= 0){ 
        return;  
    };
    this.pysayta();
    console.log('odotetaan: '+aikaAlkuun/1000+'s');
    this.marker.bindPopup('Linja: ' + this.reitti.reitinNimi + ' STOPPED. Liikkeelle klo: ' + Date.parse(lahto).toString('HH:mm'));
    if (aikaAlkuun/1000 > 60){
        this.marker.setIcon(bussiIconHarmaa);
    }
    var b = this;
    setTimeout(function(){b.kaynnista();},aikaAlkuun + 100);
};

// paivita seuraavalle pysakille
Bussi.prototype.seuraavaPysakki = function(){
    if (this.stops.pysahdykset[this.stopIndex].onkoPaate){
        this.reittiLopussa = true;
    }
    else {
	this.stopIndex++;
	this.reittiIndex++;
	this.liikuttaja = null;
	this.ehkaOdota();
    } // TODO: tee reittilopussa funktio
};

// lisaa valin reittiin
Bussi.prototype.lisaaReitinVali = function(vali) {
    if (typeof vali.coordinates == 'string'){
        var coordinates = $.parseJSON(vali.coordinates);
        vali.coordinates = coordinates;
    }
    this.reitti.pysakinValit.push(vali);
};

Bussi.prototype.poista = function(){
    bussiLayer.removeLayer(this.marker);
    console.log('poistettiin bussi: '+ this.stops.tripID);
    this.pysayta();
};

// TONOW
// jos ei reitilla, hae pysakki stopIndeksin osoittama pysakin vali
Bussi.prototype.haePysakki = function (lahto,paate,kaynnistaP) {
    var b = this;
    $.ajax({url: "get_single_route?stop1=" + lahto + "&stop2=" + paate,
            success: function(result){
                b.lisaaReitinVali(result);
                if(kaynnistaP) b.kaynnista();
	    },
            error: function(xhr, textStatus,error){
                b.poista();
		console.log('Bussi haihtui, koska ei loydetty valia pysakeille: ' + lahto + ' ja ' + paate);
                console.log(xhr);
                //epaonnistui(xhr, textStatus, error);
            },
            dataType: 'json'

           });
};

// duration sekunneissa, matka koordinaateissa, interval millisekunteja
function siirtoPerTick(duration,matka,interval){
    var siirto = matka / duration * interval / 1000;
    return siirto;
}

function etsiPysakki(reitti, pysakinId) {
    for(var i = 0; i < reitti.pysakinValit.length; i++) {
	var p = reitti.pysakinValit[i].lahtoID;
	if (p == pysakinId) return i;
    }
    return -1;
}

// stops = yhden tripId:n
function printStopTimes(stops){
    for(var i = 0; i < stops.pysahdykset.length; i++) {
        console.log('Pysakinvalin indeksi: ' + i);
        console.log('lahtoAika:' + stops.pysahdykset[i].lahtoAika);
        console.log('paateAika:' + stops.pysahdykset[i].paateAika);
        console.log('jnum: ' + stops.pysahdykset[i].jnum);
        console.log('onkolopussa:' + stops.pysahdykset[i].onkoPaate);
    }
};

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
    if(vertaaAikoja(pysahdykset[0].lahtoAika,time)){
        return 0; //aika ennen alkua
    }
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
                'marker-symbol': i,
                'marker-size': 'small'
            })
        }).addTo(stopLayer).bindPopup(parsittu.pysakinValit[i].lahtoNimi);
                //bindPopup(parsittu.pysakinValit[i].lahtoAikaTunnit + ":" + parsittu.pysakinValit[i].lahtoAikaMinuutit + " " + parsittu.pysakinValit[i].lahtoNimi);;
    }
    
    // viimeinen pysakki
    var vika = coordinates[coordinates.length-1];
    var vika1 = [vika[1],vika[0]];
    L.marker(vika1, {
        icon: L.mapbox.marker.icon({
            'marker-symbol': i,
            'marker-size': 'small'
        })
    }).addTo(stopLayer).bindPopup(parsittu.pysakinValit[i-1].paateNimi);

    var geo = {coordinates: route, type:'LineString'};
    L.geoJson(geo).addTo(routeLayer);

    var layerGroup = L.layerGroup();
    //routeLayer.addTo(layerGroup);
    //stopLayer.addTo(layerGroup);
    return([routeLayer,stopLayer]);
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
    for (var key2 in visibleRoutes) {
	poistaNakyvaReitti(visibleRoutes[key2]);
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
function lisaaReitti(reittiNro, aika, pvm, tehdaankoBussit){
    if (typeof pvm === 'undefined') pvm = {vuosi:"2015", kuukausi:"12", paiva:"07"}; // TODO: nama currentTimesta
    if (typeof aika === 'undefined'){
	aika = currentTime.toString('HH:mm:ss');
    }
    $.ajax({
        url: "/get_route?time="+aika+"&route="+reittiNro+"&year="+pvm.vuosi+"&month="+pvm.kuukausi+"&day="+pvm.paiva,
	    statusCode: {
		400: function(response) {
		    alert("Ei löydy sopivia matkoja");
		}, 4002: function(response) {
		    alert("Ei löydetä pysäkkien välistä reittiä.");
		}, 4004: function(response) {
		    alert("Haetulle ajalle ja linjalle ei löytynyt reittejä");
		}
         }, success: function(whole_result){
            var layeri_ryhma = L.layerGroup();
            for (var i = 0; i < whole_result.reitit.length; i++){
                var result = whole_result.reitit[i];
                test5 = result; //debug
                var reittiPysakit = teeReitti(result);
                for (var j = 0; j < reittiPysakit.length; j++) {
                    reittiPysakit[j].addTo(layeri_ryhma);
                }
		layeri_ryhma.addTo(reittiLayer);
		if(tehdaankoBussit) teeReitinBussit(result); // pois kommentista niin bussit piirtyvat
	     }
	     routes[reittiNro] = layeri_ryhma;
	     if(visibleRoutes.indexOf(reittiNro) == -1) {
		 visibleRoutes.push(reittiNro);
		 lisaaNakyvaReitti(reittiNro);
	     }
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
	 lisaaReitti(reittiNro,aikaTeksti,{vuosi:aika.vuosi, kuukausi: aika.kuukausi, paiva: aika.paiva});
	 //lisaaReitti(reittiNro);
     }
     else if (map.hasLayer(layer)) {
	 map.removeLayer(layer);
	 visibleRoutes.splice(visibleRoutes.indexOf(reittiNro),1);
	 poistaNakyvaReitti(reittiNro);
     } else {
	 //map.addLayer(layer);
	 layer.addTo(reittiLayer);
	 visibleRoutes.push(reittiNro);
	 lisaaNakyvaReitti(reittiNro);
     }
 }


 /// Muokkaa ajan sopivaan muotoon.
 function muokkaaAika(teksti){
    var re = /(\d\d)\.(\d\d)\.(\d\d\d\d) (\d\d?)\.(\d\d)/;//Ihanaa lukea jäkeenpäin
    var ryhmat = re.exec(teksti);
    var kuukausi;
    var paiva;
    var vuosi;
    var tunnit;
    var minuutit;
    
    if (ryhmat == null){
        var today = new Date();

        kuukausi = today.getMonth()+1;
        if (kuukausi < 10 ) kuukausi = '0' + kuukausi; 
        paiva = today.getDate();	
        if (paiva < 10) paiva = '0' + paiva;

        vuosi = today.getFullYear();

        tunnit = "11";//TODO Pohdi saisiko tästä järkevämmän ajan.
        minuutit = "00";
    }
    else {
        kuukausi = ryhmat[2];
        paiva = ryhmat[1];
        vuosi = ryhmat[3];
        tunnit = ryhmat[4];
        minuutit = ryhmat[5];
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
    reitti.addTo(reittiLayer);
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
    var date = new Date(); // on vakiona tama hetki
    dt.value = date.toString("dd.MM.yyyy HH:mm");
}

// hakee reitin stopsit ja tekee siihen bussit
function teeReitinBussit(route){
    var routeNo = route.reitinNimi;
    $.ajax({url: "get_stops?time=" + currentTime.toString('HH:mm:ss')+"&route="+routeNo,
	    success: function(result){
                stopsValmis(route,result);
	    },
	    error: function(xhr, textStatus,error){
                test2 = xhr;
		console.log('teeBussi error get_stops: var test2');
                //epaonnistui(xhr, textStatus, error);
            }
           });


}

// TONOW
function teeBussit(routeNo){
    var bareRoute = {reitinNimi:routeNo, pysakinValit:[]};
    aika = haeAnnettuAika();
    aika = muokkaaAika(aika);
    $.ajax({url: "get_stops?time=" + currentTime.toString('HH:mm:ss')+"&route="+routeNo,
	    success: function(result){
                stopsValmis(bareRoute, result);
	    },
	    error: function(xhr, textStatus,error){
                test2 = xhr;
		console.log('teeBussi error get_stops: var test2');
                //epaonnistui(xhr, textStatus, error);
            }
           });
}

function stopsValmis(route,stops){
    for(var i = 0; i < stops.matkat.length; i++) {
	var bussi = new Bussi(route, stops.matkat[i]);
        bussi.kaynnista();	    
    }
}
// http://localhost:5000/get_all_routes?date=fjfj

function paivitaAika(){
    nykyAjassa = false;
    var aika = muokkaaAika(haeAnnettuAika());
    var date = Date.parse(aika.vuosi+'.'+aika.kuukausi+'.' + aika.paiva);
    date.setHours(aika.tunnit);
    date.setMinutes(aika.minuutit);
    currentTime = date;
    nollaaKartta();
    teeKaikkiBussit();
}

function nollaaKartta(){
    map.removeLayer(reittiLayer);
    map.removeLayer(bussiLayer);
    for(var i = 0; i < bussiLista.length; i++) {
        bussiLista[i].pysayta();
    }
    reittiLayer = L.layerGroup().addTo(map);
    bussiLayer = L.layerGroup().addTo(map); // tassa layerissa on kaikki bussit
}

function teeKaikkiBussit(){
    $.ajax({url: '/get_all_routes?date=PLACEHOLDER',
	    success: function(result){
                for(var i = 0; i < result.reitit.length; i++) {
                    teeBussit(result.reitit[i]);
                }
	    },
	    error: function(xhr, textStatus,error){
		console.log('Epaonnistui get_all_routes');
                //epaonnistui(xhr, textStatus, error);
            }
           });

}
// TONOW: 
function main(){
    kelloStart();
    teeKaikkiBussit();
//    bussiLayer.addTo(map); // lisaa Bussit karttaan
    $(document).ready(function() {
	asetaNakyvaAika();
    });
}
