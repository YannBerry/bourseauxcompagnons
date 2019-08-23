// BASE MAP
    var attributionCustom = new ol.control.Attribution({
        collapsible: true
    });
    var map = new ol.Map({
        // TARGET
        target: 'locationformmap',

        // ATTRIBUTIONS OF THE BASE MAP
        controls: ol.control.defaults({attribution: false, rotate:false}).extend([attributionCustom]),

        // INTERACTIONS
        interactions: ol.interaction.defaults({
            altShiftDragRotate: false,
            pinchRotate: false
        }),

        // LAYERS
        layers: [
            new ol.layer.Tile({
                source: new ol.source.XYZ({
                    url: 'https://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png',
                    attributions: ['Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
                    ],
                })
            })
        ],

        loadTilesWhileAnimating: true,

        // VIEW (default projection is Spherical Mercator (EPSG:3857), with meters as map units)
        view: new ol.View({
            center: ol.proj.fromLonLat([7.41, 48.82]),
            zoom: 4,
            minZoom:2,
            maxZoom: 18
        })
    });

// FULLSCREEN OPTION
    map.addControl(new ol.control.FullScreen());

// GEOLOCATION
    // Creating the geolocation source included in a specific layer linked with the map
    var geolocSource = new ol.source.Vector();
    var geolocLayer = new ol.layer.Vector({
        source: geolocSource
    });
    map.addLayer(geolocLayer);
    // Create a button to allow the user to center the map on its geolocation
    const locate = document.createElement('div');
    locate.className = 'ol-control ol-unselectable locate-button';
    locate.innerHTML = '<button type="button" title="Locate me">◎</button>';
    locate.addEventListener('click', function() {
        // Defining success and error functions and the options object
        function success(pos) {
            const coords = [pos.coords.longitude, pos.coords.latitude];
            const accuracy = ol.geom.Polygon.circular(coords, pos.coords.accuracy);
            geolocSource.clear(true);
            geolocSource.addFeatures([
                new ol.Feature(accuracy.transform('EPSG:4326', map.getView().getProjection())),
                new ol.Feature(new ol.geom.Point(ol.proj.fromLonLat(coords)))
            ]);
        };
        function error(err) {
            switch(err.code) {
                case err.PERMISSION_DENIED:
                    alert("User denied the request for Geolocation.");
                    break;
                case err.POSITION_UNAVAILABLE:
                    alert("Location information is unavailable.");
                    break;
                case err.TIMEOUT:
                    alert("The request to get user location timed out.");
                    break;
                case err.UNKNOWN_ERROR:
                    alert("An unknown error occurred.");
                    break;
            }
        };
        options = {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        };
        // Activate the geolocation
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(success, error, options);
        } else {
            alert("Geolocation is not supported by this browser.");
        }
        // Zoom on the geolocation
        if (!geolocSource.isEmpty()) {
            map.getView().fit(geolocSource.getExtent(), {
                maxZoom: 10,
                duration: 500
            });
        } else {
            return false;
        }
    });
    map.addControl(new ol.control.Control({
        element: locate
    }));

// DEFINING LAYER, SOURCE & STYLE
    const profileLocIconStyle = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 1],
            anchorXUnits: 'fraction',
            anchorYUnits: 'fraction',
            src: iconMale,
            scale: 0.8,
            opacity: 1
        })
    });
    const source = new ol.source.Vector();
    const layer = new ol.layer.Vector({
        source: source,
        style: profileLocIconStyle
    });
    map.addLayer(layer);

if (locationValue) {
// DISPLAYING CURRENT LOCATION
    // ADDING THE LOCATION TO THE MAP
    const currentLocation = locationJson;
    var geojsonObject = {
        "type":"FeatureCollection",
        "features":[{
            "type": "Feature",
            "geometry": currentLocation,
            "properties": null
        }]
    };
    const locationFeatures = (new ol.format.GeoJSON({featureProjection: map.getView().getProjection()})).readFeatures(geojsonObject);
    source.addFeatures(locationFeatures);
    // INITIALIZING THE LOCATION FORM FIELD TO ITS INITIAL VALUE IF NOT NONE
    const locationGeojsonStr = (new ol.format.GeoJSON()).writeFeatures(locationFeatures); // by default dataProjection = 'EPSG:4326' in GeoJSON
    const locationGeojsonObj = JSON.parse(locationGeojsonStr);
    const locationGeojsonGeom = locationGeojsonObj.features[0].geometry;
    const locationGeojsonGeomStr = JSON.stringify(locationGeojsonGeom);
    document.getElementById('locationcoordinates').value = locationGeojsonGeomStr;
    // ZOOMING IN THE CURRENT LOCATION
    if (!source.isEmpty()) {
        map.getView().fit(source.getExtent(), {
            maxZoom: 10,
            duration: 500
        });
    }
}

// ADDING INTERACTION TO ALLOW THE USER TO MOVE THE CURRENT LOCATION
    // location_update = new ol.interaction.Modify({
    //     source: source,
    //     pixelTolerance: 30
    // });
    // map.addInteraction(location_update);

// ADDING INTERACTION TO ALLOW THE USER TO CREATE A LOCATION
    var location_draw = new ol.interaction.Draw({
        type: 'Point',
        source: source,
        style: profileLocIconStyle
    });
    map.addInteraction(location_draw);

// PASSING THE COORDINATES OF THE ADDED LOCATION TO THE DJANGO FORM
    location_draw.on("drawstart",function(e){
        source.clear();
    });
    location_draw.on("drawend",function(e){
        var writer = new ol.format.GeoJSON(); // by default dataProjection = 'EPSG:4326'
        var geojsonStr = writer.writeFeatures([e.feature]);
        var geojsonObj = JSON.parse(geojsonStr);
        var geojsonGeom = geojsonObj.features[0].geometry;
        var geojsonGeomStr = JSON.stringify(geojsonGeom);
        document.getElementById('locationcoordinates').value = geojsonGeomStr;
        // coord = e.feature.getGeometry().getCoordinates();
        // // coord = ol.proj.transform(coord, 'EPSG:3857', 'EPSG:4326');
        // // alert(coord);
        // var lon = coord[0];
        // var lat = coord[1];
        // document.getElementById('locationcoordinates').value = "POINT(" + lon + " " + lat + ")";
        // document.getElementById('locationcoordinates').value = coord;
    });
    // location_update.on("drawend",function(e){
    //     var writer = new ol.format.GeoJSON();
    //     //pass the feature as an array
    //     var geojsonStr = writer.writeFeatures([e.feature]);
    //     alert(geojsonStr);
    // });

// ADDING BUTTON TO ALLOW THE USER TO DELETE ITS LOCATION
    const deleteLocation = document.createElement('div');
    deleteLocation.className = 'ol-control ol-unselectable delete-button';
    deleteLocation.innerHTML = '<button type="button" title="Delete location">x</button>';
    deleteLocation.addEventListener('click', function() {
        source.clear();
        document.getElementById('locationcoordinates').value = null;
    });
    map.addControl(new ol.control.Control({
        element: deleteLocation
    }));