// MAPBOX APISSA LATITUDE JA LONGITUDE ON TOISINPAIN
// TODO: paivamaarat huomioon, kesa-talviaika
// onko (lon, lat) aina oikeinpain

// jquery
var $;
// L on leafletin/mapboxin maarittelema
var L;
// alustetaan kartta
L.mapbox.accessToken = 'pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q';
var map = L.mapbox.map('map', 'mikkokem.nmk0egh3');    
var tickInterval = 100; //100ms = 10fps
// debuggaukseen
var test,test2,test3,test4,test5,skewer,bussi;
// testireitti
var route = {"type":"LineString","coordinates":[[25.700226,62.252873],[25.700302,62.25277],[25.700726,62.252204],[25.70153,62.251181],[25.701641,62.250946],[25.701811,62.250824],[25.704164,62.247795],[25.704223,62.24764],[25.704378,62.247525],[25.704543,62.247552],[25.704838,62.247601],[25.705474,62.247708],[25.705142,62.248163],[25.705737,62.248268],[25.705143,62.24816],[25.705474,62.247708],[25.704838,62.247601],[25.704543,62.247552],[25.704378,62.247525],[25.705209,62.246437],[25.705275,62.24632],[25.705312,62.246203],[25.705327,62.246083],[25.705318,62.245842],[25.705242,62.245256],[25.705023,62.243766],[25.705026,62.243631],[25.704928,62.243244],[25.70482,62.242994],[25.704761,62.242742],[25.704722,62.242604],[25.704699,62.24251],[25.704887,62.242528],[25.705208,62.242542],[25.705843,62.242577],[25.707366,62.242684],[25.709942,62.242836],[25.710544,62.242829],[25.711122,62.242822],[25.711562,62.2428],[25.711969,62.242771],[25.712514,62.242669],[25.712725,62.242638],[25.713047,62.242589],[25.713238,62.242642],[25.713645,62.243105],[25.71423,62.243485],[25.714716,62.243684],[25.714896,62.2438],[25.715637,62.243998],[25.71701,62.244303],[25.718041,62.244543],[25.720037,62.245111],[25.720847,62.245252],[25.721659,62.245384],[25.722029,62.245406],[25.722457,62.245429],[25.724873,62.245414],[25.725895,62.24542],[25.726733,62.245437],[25.727113,62.245432],[25.72766,62.245449],[25.727971,62.24546],[25.728326,62.24547],[25.728268,62.245339],[25.728265,62.245255],[25.728283,62.245088],[25.728118,62.244562],[25.728092,62.244482],[25.728074,62.244426],[25.727803,62.243548],[25.727783,62.243461],[25.727992,62.243459],[25.729471,62.243398],[25.731802,62.243302],[25.732025,62.243285],[25.732177,62.243267],[25.732454,62.24324],[25.732798,62.243214],[25.734179,62.243149],[25.735582,62.243092],[25.735697,62.243072],[25.735771,62.243041],[25.735798,62.243125],[25.736008,62.244]]};

// esimerkki mapboxin vastauksesta
var original ={"origin":{"type":"Feature","geometry":{"type":"Point","coordinates":[25.700225830078125,62.252872467041016]},"properties":{"name":"Laajavuorentie"}},"destination":{"type":"Feature","geometry":{"type":"Point","coordinates":[25.70514488220215,62.24816131591797]},"properties":{"name":"Tilustie"}},"waypoints":[],"routes":[{"distance":747,"duration":61,"summary":"","geometry":{"type":"LineString","coordinates":[[25.700226,62.252873],[25.700302,62.25277],[25.700726,62.252204],[25.70153,62.251181],[25.701641,62.250946],[25.701811,62.250824],[25.704164,62.247795],[25.704223,62.24764],[25.704378,62.247525],[25.704543,62.247552],[25.704838,62.247601],[25.705474,62.247708],[25.705143,62.24816]]},"steps":[]}]};

// ALOITA OHJELMA
window.onload=main;

// taman alapuolella ei pitaisi olla muuta kuin funktioita

// piirtaa yhden reitin ja pysakit
function serveriVastasi (vastaus) {
    console.log('SUCCESS');
    //var parsittu = JSON.parse(vastaus);
    // jquery ilmeisesti parsii suoraan vastauksen
    var parsittu = vastaus;
    test=parsittu; //debug

    var route = [];
    for (var i = 0; i < parsittu.pysakinValit.length; i++) { 
        var coordinates = parsittu.pysakinValit[i].coordinates;
        route = route.concat(coordinates);
        //var geo1 = {coordinates: coordinates, type:'LineString'};
        //L.geoJson(geo1).addTo(map);

        // piirretaan markkerit
        var m1 = coordinates[0];
        var m0 = [m1[1],m1[0]];
        var marker0 = L.marker(m0, {
            icon: L.mapbox.marker.icon({
                'marker-symbol': i
            })
        }).addTo(map);
    }
    var geo = {coordinates: route, type:'LineString'};
    L.geoJson(geo).addTo(map);
    
}

// kertoo, onko kellonaika alku- ja loppuajan valilla
// function onkoAjanValilla(alku, loppu, aika) { /*implement*/}

// TODO: poista/refaktoroi
/*
function tick() {
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
*/

// WIP
// liikuttaa reitilla, reitilla monia pysakkeja
// reitti: {"reitinNimi":,"pysakinValit:
//                           [lahtoId:,lahtoNimi:,paateId:,paateNimi:,
//                            lahtoPiste,paatePiste,duration,coordinates:[]]}
var ReitillaLiikuttaja = function(reitti){
    this.reitti = reitti;
    this.pysakkino = 0;
    //this.viimeksiSiirretty = null; // TODO: tarvitaanko tata
    this.ValillaLiikuttaja = new ValillaLiikuttaja(reitti[0].pysakinValit[this.reittino].coordinates);
};

// palauta [uusi-sijainti, onko-pysakilla]
ReitillaLiikuttaja.prototype.liikuta = function(matka){
        if (this.viimeksiSiirretty === null){
            this.viimeksiSiirretty = date;
        }
        // etsi aikaa vastaava reitin piste
        // muokkaa rettino
    };


// reitti: {"reitinNimi":,"pysakinValit:
//                           [lahtoId:,lahtoNimi:,paateID:,paateNimi:,
//                            lahtoPiste,paatePiste,duration,coordinates:[]]}
// stops: {"reitinNimi":, "matkat":
//                           [ {tripId,pysahdykset:[{lahtoID,paateID,lahtoAika,paateAika}]} ]
//
var Bussi = function(tripId, reittiArg, stops){
    this.reitti = reittiArg;
    console.log('reittiarg:');
    console.log(reittiArg);
    this.sijainti = [0,0];
    this.liikuttaja = null;
    this.stops = stops;
    this.stopIndex = 0;            // monennellako pysakilla reitilla
    this.stopsLopussa = false;
    this.onkoLiikeessa = false;
    this.reittiLopussa = false;
    this.marker = L.marker([0,0]).addTo(map);
    
};

// TODO
// hakee lisaa stopseja reitille (mahdollisesti korvaa kokonaan)
Bussi.prototype.stopsLopussa = function(){
    
};

Bussi.prototype.tick = function(){
    if (this.tarkistaLahto()) {

        var coordinates = this.reitti.pysakinValit[this.stopIndex].coordinates;
        test = this.reitti;
        if (this.liikuttaja === null){
            this.liikuttaja = new ValillaLiikuttaja(coordinates);
            this.sijainti = coordinates[this.stopIndex];
            this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
            console.log('alustettiin bussi!');
        } else {
            var siirto = this.liikuttaja.siirra(0.00000001); // [pos,jalella,perillaP]
            this.sijainti = siirto;
            this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
            console.log('siirrettiin: ' + this.sijainti);
        }
        
    }
    console.log('timeouttiin');
    setTimeout(this.tick(),4000); //tickinterval
};

// tarkistaa milloin lahdetaan pysakilta
// ottaa varmaan ajan
Bussi.prototype.tarkistaLahto = function(date, leave){
//    if (date >= leave){
        return true;
//    }
//    return false;
};

// TODO testaa
// etsii oikean pysakin, palauttaa indeksin tai -1 jos ei loydy
function etsiAika(stops,time){
    var pysahdykset = this.stops.pysahdykset; //taulukko
    for(var i = 0; i < pysahdykset.length; i++){
        if(timeCompare(time, pysahdykset[i].lahtoAika)){
	    if (i===0) return 0;
            return i-1;
        }
    }
    return -1;
}


/**
 * palauta true jos time1 suurempi tai yhtasuuri kuin time2
 *  time hh:mm:ss/ h:m:s
 */
function timeCompare(time1, time2){
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

    // palauta uusi sijainti
    // muuta sijaintia ja indeksia
    
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
            if (this.seuraavanIndeksi >= this.reitti.length - 1)
                return [this.reitti[this.seuraavanIndeksi],matkaaJaljella,true]; //perilla
            matkaaJaljella = -matkaaJaljella;
            this.sijainti = this.reitti[this.seuraavanIndeksi];
            this.seuraavanIndeksi++;
            
            continue;
        }
        console.log('seuraavanIndeksi: ');
        console.log(this.seuraavanIndeksi);
        console.log('length: ');
        console.log(this.reitti.length);
        var uusiSijainti = liikuKohti(this.sijainti,kohde,matka); // TODO TODO: tassa kutsussa saattaa olla vika
        console.log('uusijainti: '+uusiSijainti);
        this.sijainti = uusiSijainti;
        return [uusiSijainti, matkaaJaljella, false]; // ei perilla
    }
};
//funtion /

/*************** Puhtaat funktiot ******************/

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


var reitti = {
    "reitinNimi": "27",
    "pysakinValit": [{
        "lahtoPiste": "koordinaatit",
        "paatePiste": "koordinaatit",
        "coordinates": [['koordinaatit'],['koordinaatit']]
    }]
};


var stopit = {
    "reitinNimi": "27",
    "pysahdykset": [{
        "lahtoID": 'id',
        "lahtoNimi": "nimi",
        "paateID": 'id',
        "paateNimi": 'nimi',
        "lahtoAika": "12:30",
        "paateAika": "12:31",
        "duration": 300
    }]};

function epaonnistui(xhr, textStatus, error){
    console.log(xhr.url);
    console.log(textStatus);
    console.log(error);
}

function main(){
    //alustaKartta();
    console.log('ALKU');
    
    //get_stops
    /*
    $.ajax({url: "get_stops?time=12:30:00&route=18",
            success: function(result){
                test2 = result;},
            error: function(xhr, textStatus,error){
                test2 = xhr;
                epaonnistui(xhr, textStatus, error);
            }
           });
    //*/
    //get_route
    $.ajax({
        url: "/get_route?time=18:00:00&route=18",
        success: function(result){
            serveriVastasi(result);
            test3=result;
            var b = new Bussi(1234, result, []);
            bussi = b;
            b.tick();
        },
        dataType: 'json',
        error: epaonnistui
    });
    //*/

    console.log('loppu');
    
}

//bussi = function(tripId, reitti, stops){
