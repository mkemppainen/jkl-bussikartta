//global kommentin tarvii, ettei emacs herjaa alustamattomista muuttujista
/* global $, L, timeOut, setInterval*/
// MAPBOX APISSA LATITUDE JA LONGITUDE ON TOISINPAIN
// TODO: paivamaarat huomioon, kesa-talviaika
// onko (lon, lat) aina oikeinpain

// alustetaan kartta
L.mapbox.accessToken = 'pk.eyJ1IjoibWlra29rZW0iLCJhIjoiY2lmcDIwMDNlMDFpMnRha251dHgwbG9hZiJ9.9DLJHVEwbRf7xT0WkFqj5Q';
var map = L.mapbox.map('map', 'mikkokem.nmk0egh3');    
var featureLayer = L.mapbox.featureLayer();
var tickInterval = 100; //100ms = 10fps
var test,test2,test3,test4,test5,skewer,bussi;

// ALOITA OHJELMA
window.onload=main;

// taman alapuolella ei pitaisi olla muuta kuin funktioita

// piirtaa yhden reitin ja pysakit
function serveriVastasi (vastaus) {
    console.log('SUCCESS');
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
        }).addTo(featureLayer);
    }
    var geo = {coordinates: route, type:'LineString'};
    L.geoJson(geo).addTo(featureLayer);

    featureLayer.addTo(map);
}

// reitti: {"reitinNimi":,"pysakinValit:
//                           [lahtoId:,lahtoNimi:,paateID:,paateNimi:,
//                            lahtoPiste,paatePiste,duration,coordinates:[]]}
// stops: {"reitinNimi":, "matkat":
//                           [ {tripId,pysahdykset:[{lahtoID,paateID,lahtoAika,paateAika}]} ]
var Bussi = function(tripId, reittiArg, stops){
    this.reitti = reittiArg;
    this.sijainti = [0,0];
    this.liikuttaja = null;
    this.stops = stops;
    this.stopIndex = 0;            // monennellako pysakilla reitilla
    this.stopsLopussa = false;
    this.onkoLiikeessa = false;
    this.reittiLopussa = false;
    this.marker = L.marker([0,0]).addTo(featureLayer);
    
};

// TODO
// hakee lisaa stopseja reitille (mahdollisesti korvaa kokonaan)
Bussi.prototype.stopsLopussa = function(){
    
};

// tarkistaa milloin lahdetaan pysakilta
// ottaa varmaan ajan
Bussi.prototype.tarkistaLahto = function(date, leave){
//    if (date >= leave){
    return true;
//    }
//    return false;
};

Bussi.prototype.tick = function(){
    if (this.reittiLopussa) return;
    if (this.tarkistaLahto('date','leave')) { //todo: oikeat argumentit

        var coordinates = this.reitti.pysakinValit[this.stopIndex].coordinates;
        test = this.reitti;
        if (this.liikuttaja === null){
            this.liikuttaja = new ValillaLiikuttaja(coordinates);
            this.sijainti = coordinates[0];
            this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
        } else {
            var siirto = this.liikuttaja.siirra(0.0002); // [pos,jalella,perillaP] //TODO siirtoon oikea matka MEMO siirtonopeus
            this.sijainti = siirto[0];
            this.marker.setLatLng(L.latLng(this.sijainti[1],this.sijainti[0]));
	    if (siirto[2]) this.seuraavaPysakki();

        }   
    }; //if loppu
};

// paivita seuraavalle pysakille
Bussi.prototype.seuraavaPysakki = function(){
    if (this.stopIndex < this.reitti.pysakinValit.length - 1)this.stopIndex++;
    else { this.reittiLopussa = true; }
    this.liikuttaja = null;//new ValillaLiikuttaja(this.reitti.pysakinValit[this.stopIndex].coordinates);
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
            if (this.seuraavanIndeksi >= this.reitti.length - 1){
		var palautus = [this.reitti[this.seuraavanIndeksi],matkaaJaljella,true]; //perilla
                return palautus;
	    }
            matkaaJaljella = -matkaaJaljella;
            this.sijainti = this.reitti[this.seuraavanIndeksi];
            this.seuraavanIndeksi++;
            
            continue;
        }

        var uusiSijainti = liikuKohti(this.sijainti,kohde,matka); // TODO TODO: tassa kutsussa saattaa olla vika
        this.sijainti = uusiSijainti;
        return [uusiSijainti, matkaaJaljella, false]; // ei perilla
    }
};

/*************** Puhtaita funktiot ******************/

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
    alert("Kutsuttiin tyhjennystä");
    map.removeLayer(featureLayer);
    featureLayer = L.mapbox.featureLayer();
}

// kutsutaan html:sta
function testiPiirto(linja){
    $.ajax({
        url: "/get_route?time=18:00:00&route=" + linja,
        success: function(result){
            console.log('Succes');
            serveriVastasi(result);
            test3=result;
            var b = new Bussi(1234, result, []);
            bussi = b;
	    setInterval(function(){b.tick();},100);
        },
        dataType: 'json',
        error: epaonnistui
    });

}

function main(){

    $.ajax({url: "get_stops?time=12:30:00&route=18",
            success: function(result){
                test2 = result;
		console.log('success get_stops: test2');
	    },
	    
            error: function(xhr, textStatus,error){
                test2 = xhr;
		console.log('error get_stops: test2');
                //epaonnistui(xhr, textStatus, error);
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
	    setInterval(function(){b.tick();},100);
        },
        dataType: 'json',
        error: epaonnistui
    });

    console.log('mainin loppu');
}
