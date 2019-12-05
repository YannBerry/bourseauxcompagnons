// BASE MAP
    const aAttributionCustom = new ol.control.Attribution({
        collapsible: true
    });
    const amap = new ol.Map({
        // TARGET
        target: 'availabilityformmap',

        // ATTRIBUTIONS OF THE BASE MAP
        controls: ol.control.defaults({attribution: false, rotate:false}).extend([aAttributionCustom]),

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
    amap.addControl(new ol.control.FullScreen());

// GEOLOCATION
    // Creating the geolocation source included in a specific layer linked with the map
    const ageolocSource = new ol.source.Vector();
    const ageolocLayer = new ol.layer.Vector({
        source: ageolocSource
    });
    amap.addLayer(ageolocLayer);
    // Create a button to allow the user to center the map on its geolocation
    const alocate = document.createElement('div');
    alocate.className = 'ol-control ol-unselectable locate-button';
    alocate.innerHTML = '<button type="button" title="Locate me">◎</button>';
    alocate.addEventListener('click', function() {
        // Defining success and error functions and the options object
        function success(pos) {
            const coords = [pos.coords.longitude, pos.coords.latitude];
            const accuracy = ol.geom.Polygon.circular(coords, pos.coords.accuracy);
            ageolocSource.clear(true);
            ageolocSource.addFeatures([
                new ol.Feature(accuracy.transform('EPSG:4326', amap.getView().getProjection())),
                new ol.Feature(new ol.geom.Point(ol.proj.fromLonLat(coords)))
            ]);
            // Zoom on the geolocation
            if (!ageolocSource.isEmpty()) {
                amap.getView().fit(ageolocSource.getExtent(), {
                    maxZoom: 10,
                    duration: 500
                });
            } else {
                alert("Issue in assigning geoloc features to geoloc source in openlayers.")
            }
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
    });
    amap.addControl(new ol.control.Control({
        element: alocate
    }));

// DEFINING LAYER, SOURCE
    const areaSource = new ol.source.Vector();
    const areaLayer = new ol.layer.Vector({
        source: areaSource
    });
    amap.addLayer(areaLayer);


// DISPLAYING CURRENT AREA (when drawMyArea function is called)
    function drawMyArea(AreaGeoJson) {
        // ADDING THE AVAILABILITY AREA TO THE MAP
        const geojsonObject = {
            "type": "Feature",
            "geometry": AreaGeoJson, // srid: 4326
            "properties": {}
        };
        const areaFeatures = (new ol.format.GeoJSON({featureProjection: amap.getView().getProjection()})).readFeatures(geojsonObject);
        areaSource.addFeatures(areaFeatures);
        // INITIALIZING THE AVAILABILITY_AREA_GEO FORM FIELD TO ITS INITIAL VALUE IF NOT NONE
        const areaGeojsonStr = (new ol.format.GeoJSON({featureProjection: amap.getView().getProjection(), dataProjection: 'EPSG:4326'})).writeFeatures(areaFeatures); // by default dataProjection = 'EPSG:4326' in GeoJSON
        const areaGeojsonObj = JSON.parse(areaGeojsonStr);
        const areaGeojsonGeom = areaGeojsonObj.features[0].geometry;
        const areaGeojsonGeomStr = JSON.stringify(areaGeojsonGeom);
        document.getElementById('areacoordinates').value = areaGeojsonGeomStr;
        // ZOOMING IN THE CURRENT LOCATION
        if (!areaSource.isEmpty()) {
            amap.getView().fit(areaSource.getExtent(), {
                maxZoom: 10,
                duration: 500
            });
        } else {
            alert("Issue in assigning geoloc features to geoloc source in openlayers.")
        }
    }

// // ADDING INTERACTION TO ALLOW THE USER TO ALTER THE CURRENT AREA
//     amap.addInteraction(new ol.interaction.Modify({
//         source: areaSource
//     }));
    
// ADDING INTERACTION TO ALLOW THE USER TO CREATE AN AREA
    const area_draw = new ol.interaction.Draw({
        type: 'Polygon',
        source: areaSource
    });
    amap.addInteraction(area_draw);

// GETTING THE COORDINATES OF THE ADDED AREA
    area_draw.on("drawstart",function(e){
        areaSource.clear();
    });
    area_draw.on("drawend",function(e){
        const writer = new ol.format.GeoJSON({featureProjection: amap.getView().getProjection(), dataProjection: 'EPSG:4326'}); // by default dataProjection = 'EPSG:4326'
        // pass the feature as an array
        const geojsonStr = writer.writeFeatures([e.feature]);
        const geojsonObj = JSON.parse(geojsonStr);
        const geojsonGeom = geojsonObj.features[0].geometry;
        const geojsonGeomStr = JSON.stringify(geojsonGeom);
        document.getElementById('areacoordinates').value = geojsonGeomStr;
    });

// ADDING BUTTON TO ALLOW THE USER TO DELETE ITS AVAILABILITY AREA
    const deleteArea = document.createElement('div');
    deleteArea.className = 'ol-control ol-unselectable delete-button';
    deleteArea.innerHTML = '<button type="button" title="Delete area">x</button>';
    deleteArea.addEventListener('click', function() {
        areaSource.clear();
        document.getElementById('areacoordinates').value = null;
    });
    amap.addControl(new ol.control.Control({
        element: deleteArea
    }));

// UPLOAD AREA DRAGGING IN GEOJSON FILE IN THE MAP
    amap.addInteraction(new ol.interaction.DragAndDrop({
        source: areaSource,
        formatConstructors: [ol.format.GeoJSON]
    }));

// // DOWNLOAD THE POLYGON DRAWN
//     const downloadArea = document.createElement('div');
//     downloadArea.className = 'ol-control ol-unselectable locate-button';
//     downloadArea.innerHTML = '<a id="download" download="features.json"><button type="button" title="Download area">-></button></a>';
//     downloadArea.addEventListener('click', function() {
//         const format = new ol.format.GeoJSON({featureProjection: 'EPSG:3857'});
//         const download = document.getElementById('download');
//         areaSource.on('change', function() {
//             const features = areaSource.getFeatures();
//             const json = format.writeFeatures(features);
//             download.href = 'data:text/json;charset=utf-8,' + json;
//         });
//     });
//     amap.addControl(new ol.control.Control({
//         element: downloadArea
//     }));