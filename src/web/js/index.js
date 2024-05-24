var mymap;
var sobj;
var sfile;
var sbuf;

function render() {
    mymap = L.map('mapid').setView([-84.3, 33.77], 12);
    sobj = new L.Shapefile("exdata/roadshp.zip",
			   {
			       pointToLayer: function(gpoint, coord) {
				   console.log(coord, gpoint);
				   return L.marker(coord);
			       },
			       isArrayBuffer : false,
			       color: 'red',
			       onEachFeature: function(feature, layer) {
				   console.log(feature, layer);
			       }
			   });
    sobj.addTo(mymap);
    sobj.once("data:loaded", function() {
	console.log("finished loaded shapefile");
    });
}


function loadSHP(input) {
    sfile = input.files[0];
    console.log(input.files[0]);
    var reader = new FileReader();
    reader.onload = function() {
	var promise = new Promise(function(res, rej) {
	    sbuf = reader.result; res(sbuf);
	})
	    .finally(
		function() {
		    console.log("finally");
		    sobj = new L.Shapefile(sbuf,{
			isArrayBuffer : true,
			color: 'red',
			onEachFeature: function(feature, layer) {
			    console.log(feature, layer);
			}
		    });
		    sobj.addTo(mymap);
		    sobj.once("data:loaded", function() {
			console.log("finished loaded shapefile");
		    });
		});
	return promise;
    };
    reader.readAsArrayBuffer(sfile);
}
