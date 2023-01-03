// --------------------------------------------------------------------------------//
                            // Init Basemaps Section: //
// --------------------------------------------------------------------------------//

var osmMap = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png');
var stamenMap = L.tileLayer.provider('Stamen.Watercolor');
var esriMap = L.tileLayer.provider('Esri.WorldImagery');

window.onload = function() {
    var map = L.map('map', {
        layers: [esriMap, econLayer1]
    }).setView([51.6978162, 5.3036748], 13);
    new OSMBuildings(map).load('https://{s}.data.osmbuildings.org/0.2/anonymous/tile/{z}/{x}/{y}.json'); }

// --------------------------------------------------------------------------------//
            // Init Geoserver, server and workspace connection Section: //
// --------------------------------------------------------------------------------//

var geoServerIPPort = 'localhost:8085';
var geoServerWorkspace = 'greenman';



// --------------------------------------------------------------------------------//
                            // Add wms layers Section: //
// --------------------------------------------------------------------------------//

var LayerName1 = 'no_scenario';
var econLayer1 = L.tileLayer.betterWms(
    "http://" + geoServerIPPort + "/geoserver/" + geoServerWorkspace + "/wms",
    {
        layers: LayerName1,
        format: "image/png",
        transparent: true,
        version: "1.1.0",
        tiled: false,


    }
)

var LayerName2 = 'random_raster';
var econLayer2 = L.tileLayer.betterWms(
    "http://" + geoServerIPPort + "/geoserver/" + geoServerWorkspace + "/wms",
    {
        layers: LayerName2,
        format: "image/png",
        transparent: true,
        version: "1.1.0",
        tiled: false,


    }
)

// window.onload = function() {
// var map = L.map('map', {
//     layers: [esriMap, econLayer1]
// }).setView([51.6978162, 5.3036748], 13);
// new OSMBuildings(map).load('https://{s}.data.osmbuildings.org/0.2/anonymous/tile/{z}/{x}/{y}.json'); }
var baseMaps = {
    OSM: osmMap,
    'Stamen Watercolor': stamenMap,
    'World Imagery': esriMap
}

var overlayMaps = {
    "nul-meting": econLayer1,
    "scenario 1": econLayer2

};
var mapLayers = L.control.layers(baseMaps, overlayMaps).addTo(map);
L.control.sideBySide(econLayer1, econLayer2).addTo(map)
var customMarker= L.Icon.extend({
    options: {
        shadowUrl: null,
        iconAnchor: new L.Point(12, 12),
        iconSize: new L.Point(24, 24),
        iconUrl: 'pngtree.png'
    }
});

// --------------------------------------------------------------------------------//
                             // Draw Shapes Section: //
// --------------------------------------------------------------------------------//

var drawnItems = new L.FeatureGroup();

map.addLayer(drawnItems)

var drawControl = new L.Control.Draw({
    draw: {
        circle: false,
        marker: {
            icon: new customMarker()
        },
        polyline: false, 
        polygon: false,
        rectangle: false,
        circlemarker: false

    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

map.on('draw:created', function (e) {
    var type = e.layerType,
    layer = e.layer;
    var tempMarker = drawnItems.addLayer(layer);
    var shape = layer.toGeoJSON()
    
    drawnItems.addLayer(layer);
    console.log("layer Type:")
    console.log(type)
    console.log("\n")
    console.log("Geometry object:")
    console.log(layer)
    console.log("\n")
    console.log("GeoJSON object:")
    console.log(shape)
    

    var latitude=layer.getLatLng().lat;
    var longitude=layer.getLatLng().lng;



// --------------------------------------------------------------------------------//
                     // Create html-form within popup Section: //
// --------------------------------------------------------------------------------//
    var popupContent = '<form role="form" id="form" enctype="multipart/form-data" class = "form-horizontal">'
    +  
    '<div class="form-group">'
    +
        '<label for="shaduwtijd" class="control-label col-sm-5">Datum en tijd</label>'
        +
        '<input type="datetime-local" id="shaduwtijd" name="shaduwtijd" value="2022-07-01T15:00" min="2022-01-01T00:00" max="2022-012-31T00:00" class="form-control"/>'
        + 
    '</div>'
    +
    '<div class="form-group">'
    +
        '<label for="kroon_hoogte" class="control-label col-sm-5">Boomkroon hoogte</label>'
        +
        '<input type="text" placeholder="bv: 2.2 m" id="kroon_hoogte" name="kroon_hoogte" class="form-control"/>'
        + 
    '</div>'
    +
    '<div class="form-group">'
    +
        '<label for="kroon_diameter" class="control-label col-sm-5">Boomkroon diameter</label>'
        +
        '<input type="text" placeholder="bv: 1.6 meter" id="kroon_diameter" name="kroon_diameter" class="form-control"/>'
        + 
    '</div>'
    +
    '<div class="form-group">'
    +
        '<label for="stam_hoogte" class="control-label col-sm-5">Boom(stam) hoogte</label>'
        +
        '<input type="text" placeholder="bv: 4 meter " id="stam_hoogte" name="stam_hoogte" class="form-control"/>'
        + 
    '</div>'
    +
    '<div class="form-group">'
    +
        '<label for="LAI" class="control-label col-sm-5" id=lailab >Blad dichtheid (schaal 1/10)</label>'
        +
        '<input type="range" placeholder="1/10" id="lai" name="LAI" class="form-control" min="0" max="10"/>'
        + 
    '</div>'
    +
    '<input style="display: none;" type="text" id="lat" name="lat" value="'
    +
    latitude.toFixed(6)+'" />'
    +
    '<input style="display: none;" type="text" id="lng" name="lng" value="'
    +
    longitude.toFixed(6)
    +
    '" />'
    +
    '<div class="form-group">'
    +
      '<div style="text-align:center;" class="col-xs-4 col-xs-offset-2"><button type="button" class="btn">Cancel</button></div>'  
      +
      '<div style="text-align:center;" class="col-xs-4"><button id="submit" value="submit" class="btn btn-primary trigger-submit">Submit</button></div>'
      +
    '</div>'
    +
    '</form>';
    tempMarker.bindPopup(popupContent,{
      keepInView: true,
      closeButton: false
      }).openPopup();

    $("#submit").click(function(e){
        alert( "je staat op het punt een nieuwe turbine toe te voegen.. " ) 
        e.preventDefault();
        let postData = {
            'datumtijd': $("#shaduwtijd").val(),
            'kroonh': $("#kroon_hoogte").val(),
            'kroondia': $("#kroon_diameter").val(),
            'stamh': $("#stam_hoogte").val(),
            'bladindex': $("#lai").val(),
            'xcoord': longitude,
            'ycoord': latitude
        };

        $.ajax({
            url: 'writePointData.php',
            method: 'post',
            data: postData
        }).done(function(data){
            console.log(data);
            if (data == 1) {
                alert("punt is toegevoegd");
                // updatePoints();
            }
            else {
                alert ('Er is iets fout gegaan');
            }
        })

      
  });
});



// map.on('dblclick', function(evt){
//     console.log(evt);
//     let naam = prompt("Geef een naam:");


    



