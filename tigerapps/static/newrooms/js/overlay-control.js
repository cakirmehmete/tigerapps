/* global OverlayControl */
OverlayControl = L.Control.extend({
    options: {
        position: 'topright'
    },

    onAdd: function (map) {
        // create the control container with a particular class name
        var building_id = this.options.building_id;
        var floor_id = this.options.floor_id;
        var container = L.DomUtil.create('div', 'overlay-control');
        var backLink = L.DomUtil.create('a', 'overlay-link btn btn-warning btn-raised');
        backLink.innerText = "Back To Map";
        backLink.onclick = function() {setMapView()};
        
        container.appendChild(backLink);
        var title = L.DomUtil.create('h3', 'overlay-header');
        title.innerText = buildings[building_id].name;
        container.appendChild(title);
        
        
        for (var j = 0; j < this.floorOrdering.length; j++) {
            for (var i = 0; i < buildings[building_id].floors.length; i++) {
                if (this.floorOrdering[j] != buildings[building_id].floors[i]) continue;
                var link = L.DomUtil.create('a', 'overlay-link');
                link.innerText = this.floorMapping[buildings[building_id].floors[i]];
                if (buildings[building_id].floors[i] == floor_id) {
                    link.className += " overlay-link-selected";
                }
                else {
                    link.onclick = function(i) {
                        return function () {
                            setMapView(building_id + "-" + buildings[building_id].floors[i])
                        }
                    }(i);
                }
                container.appendChild(link);
            }
        }
        
        return container;
    },
    
    floorMapping: {
        "A": "A Level",
        "01": "1st Floor",
        "02": "2nd Floor",
        "03": "3rd Floor",
        "04": "4th Floor",
        "05": "5th Floor",
        "06": "6th Floor",
        "00": "Ground Floor",
        "3M": "3rd Floor Mezzanine",
        "4M": "4th Floor Mezzanine"
    },
    
    floorOrdering: ["A", "00", "01", "02", "03", "3M", "04", "4M", "05", "06"]
    
});