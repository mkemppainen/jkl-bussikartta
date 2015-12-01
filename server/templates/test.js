/* global map, $, featureLayer, ValillaLiikuttaja */
// kartta
// map;

// heittaa virheen, jos testi menee pieleen
function assert(condition, message) {
    if (!condition) {
        message = message || "Assertion failed";
        if (typeof Error !== "undefined") {
            throw new Error(message);
        }
        throw message; // Fallback
    }
}

function tests(){
//    console.l
    
    valillaLiikuttajaTesti();
}

function valillaLiikuttajaTesti(){
    var fail = []; // listaan failattujen testien numerot
    var vali = [[1,2],[2,2],[5,2],[0,2],[0,0]];
    var liikuttaja = new ValillaLiikuttaja(vali);
    liikuttaja.siirra(1);
    // todo: testaa liikutaa monta kertaa
}
