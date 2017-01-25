/* global OverlayControl */
LegendControl = L.Control.extend({
    options: {
        position: 'topright'
    },

    onAdd: function (map) {
        // create the control container with a particular class name
        var building_id = this.options.building_id;
        var floor_id = this.options.floor_id;
        var container = L.DomUtil.create('div', 'overlay-control legend');
        var title = L.DomUtil.create('h3', 'overlay-header');
        title.innerText = "Color Legend";
        container.appendChild(title);
        var colors = {
            butler: "#0068AC",
            whitman : "#89CCE2",
            rockefeller : "#6EB43F",
            mathey: "#941e00",
            forbes: "#EF4035",
            wilson: "#F8981D",
            upperclass: "#828282"
        }
        
        for (var j in colors) {
            var swatch = L.DomUtil.create('span', 'color-swatch');
            swatch.style.background = colors[j];
            container.appendChild(swatch);
            var name = L.DomUtil.create('span', 'title');
            name.innerText = j[0].toUpperCase() + j.slice(1);
            container.appendChild(name);
            container.appendChild(L.DomUtil.create('br'))
        }
        
        return container;
    }
    
});